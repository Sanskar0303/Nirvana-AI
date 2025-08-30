import os
from dotenv import load_dotenv
import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path as PathLib
import json
import asyncio
import config  # Your server's fallback config
from typing import Type, List, Optional
import base64
import websockets
from datetime import datetime
import re

import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    TerminationEvent,
    TurnEvent,
)
import google.generativeai as genai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI()

BASE_DIR = PathLib(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


async def get_llm_response_stream(transcript: str, client_websocket: WebSocket, chat_history: List[dict], user_keys: dict):
    if not transcript or not transcript.strip():
        return

    gemini_api_key = user_keys.get("gemini_api_key")
    murf_api_key = user_keys.get("murf_api_key")
    # tavily_api_key = user_keys.get("tavily_api_key") # Ready for future use

    if not gemini_api_key:
        logging.error("Cannot get LLM response because Gemini API key is missing.")
        await client_websocket.send_text(json.dumps({"type": "error", "message": "Gemini API key is missing."}))
        return

    try:
        genai.configure(api_key=gemini_api_key)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        logging.error(f"Failed to initialize Gemini model: {e}")
        await client_websocket.send_text(json.dumps({"type": "error", "message": f"Invalid Gemini API Key."}))
        return

    logging.info(f"Sending to Gemini with history: '{transcript}'")
    
    murf_uri = f"wss://api.murf.ai/v1/speech/stream-input?api-key={murf_api_key}&sample_rate=44100&channel_type=MONO&format=MP3"
    
    try:
        async with websockets.connect(murf_uri) as websocket:
            voice_id = "en-US-natalie"
            logging.info(f"Successfully connected to Murf AI, using voice: {voice_id}")
            
            context_id = f"voice-agent-context-{datetime.now().isoformat()}"
            
            config_msg = {
                "voice_config": {"voiceId": voice_id, "style": "Conversational"},
                "context_id": context_id
            }
            await websocket.send(json.dumps(config_msg))

            async def receive_and_forward_audio():
                first_audio_chunk_received = False
                while True:
                    try:
                        response_str = await websocket.recv()
                        response = json.loads(response_str)

                        if "audio" in response and response['audio']:
                            if not first_audio_chunk_received:
                                await client_websocket.send_text(json.dumps({"type": "audio_start"}))
                                first_audio_chunk_received = True
                                logging.info("✅ Streaming first audio chunk to client.")

                            base_64_chunk = response['audio']
                            await client_websocket.send_text(
                                json.dumps({"type": "audio", "data": base_64_chunk})
                            )

                        if response.get("final"):
                            logging.info("Murf confirms final audio chunk received. Sending audio_end to client.")
                            await client_websocket.send_text(json.dumps({"type": "audio_end"}))
                            break
                    except websockets.ConnectionClosed as e:
                        logging.warning(f"Murf connection closed unexpectedly: {e.code} {e.reason}")
                        if "authentication failed" in str(e.reason).lower():
                             await client_websocket.send_text(json.dumps({"type": "error", "message": "Murf.ai authentication failed. Check API key."}))
                        await client_websocket.send_text(json.dumps({"type": "audio_end"}))
                        break
                    except Exception as e:
                        logging.error(f"Error in Murf receiver task: {e}")
                        break
            
            receiver_task = asyncio.create_task(receive_and_forward_audio())

            try:
                prompt = f"""You are Nirvana, an AI voice assistant... [Your prompt remains the same] ...IMPORTANT: Do not use any markdown formatting. Provide only plain text."""
                
                chat_history.append({"role": "user", "parts": [prompt]})
                chat = gemini_model.start_chat(history=chat_history[:-1])
                def generate_sync(): return chat.send_message(prompt, stream=True)
                loop = asyncio.get_running_loop()
                gemini_response_stream = await loop.run_in_executor(None, generate_sync)

                sentence_buffer, full_response_text = "", ""
                print("\n--- DIVA (GEMINI) STREAMING RESPONSE ---")
                for chunk in gemini_response_stream:
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                        full_response_text += chunk.text
                        await client_websocket.send_text(json.dumps({"type": "llm_chunk", "data": chunk.text}))
                        
                        sentence_buffer += chunk.text
                        sentences = re.split(r'(?<=[.?!])\s+', sentence_buffer)
                        
                        if len(sentences) > 1:
                            for sentence in sentences[:-1]:
                                if sentence.strip():
                                    await websocket.send(json.dumps({"text": sentence.strip(), "end": False, "context_id": context_id}))
                            sentence_buffer = sentences[-1]

                if sentence_buffer.strip():
                    await websocket.send(json.dumps({"text": sentence_buffer.strip(), "end": True, "context_id": context_id}))
                
                chat_history.append({"role": "model", "parts": [full_response_text]})

                print("\n--- END OF DIVA (GEMINI) STREAM ---\n")
                logging.info("Finished streaming to Murf. Waiting for final audio chunks...")
                await asyncio.wait_for(receiver_task, timeout=60.0)
                logging.info("Receiver task finished gracefully.")
            
            finally:
                if not receiver_task.done():
                    receiver_task.cancel()
                    logging.info("Receiver task cancelled on exit.")

    except asyncio.CancelledError:
        logging.info("LLM/TTS task was cancelled by user interruption.")
        await client_websocket.send_text(json.dumps({"type": "audio_interrupt"}))
    except websockets.exceptions.InvalidURI:
        logging.error("Invalid Murf API URI, likely due to a missing API key.")
        await client_websocket.send_text(json.dumps({"type": "error", "message": "Murf.ai API key is missing or invalid."}))
    except Exception as e:
        logging.error(f"Error in LLM/TTS streaming function: {e}", exc_info=True)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

async def send_client_message(ws: WebSocket, message: dict):
    try:
        await ws.send_text(json.dumps(message))
    except ConnectionError:
        logging.warning("Client connection closed, could not send message.")

@app.websocket("/ws")
async def websocket_audio_streaming(websocket: WebSocket):
    await websocket.accept()
    logging.info("WebSocket connection accepted. Waiting for API key configuration.")
    main_loop = asyncio.get_running_loop()
    
    llm_task, last_processed_transcript, chat_history, user_keys = None, "", [], {}
    
    try:
        config_data = json.loads(await websocket.receive_text())
        if config_data.get("type") == "config":
            user_keys['assemblyai_api_key'] = config_data.get("assemblyai_api_key") or getattr(config, 'ASSEMBLYAI_API_KEY', None)
            user_keys['gemini_api_key'] = config_data.get("gemini_api_key") or getattr(config, 'GEMINI_API_KEY', None)
            user_keys['murf_api_key'] = config_data.get("murf_api_key") or getattr(config, 'MURF_API_KEY', None)
            user_keys['tavily_api_key'] = config_data.get("tavily_api_key") or getattr(config, 'TAVILY_API_KEY', None)
            logging.info("API key configuration received from client.")
        else:
            raise ValueError("First message was not a config message.")
    except (json.JSONDecodeError, ValueError, WebSocketDisconnect) as e:
        logging.error(f"Failed to receive valid config from client: {e}")
        await send_client_message(websocket, {"type": "error", "message": "Server did not receive API key configuration."})
        await websocket.close(code=1000)
        return

    assemblyai_api_key = user_keys.get("assemblyai_api_key")
    if not assemblyai_api_key:
        logging.error("ASSEMBLYAI_API_KEY not configured")
        await send_client_message(websocket, {"type": "error", "message": "AssemblyAI API key not configured."})
        await websocket.close(code=1000)
        return

    client = StreamingClient(StreamingClientOptions(api_key=assemblyai_api_key))

    def on_turn(self: Type[StreamingClient], event: TurnEvent):
        nonlocal last_processed_transcript, llm_task
        transcript_text = event.transcript.strip()
        
        if event.end_of_turn and event.turn_is_formatted and transcript_text and transcript_text != last_processed_transcript:
            last_processed_transcript = transcript_text
            if llm_task and not llm_task.done():
                llm_task.cancel()
                asyncio.run_coroutine_threadsafe(send_client_message(websocket, {"type": "audio_interrupt"}), main_loop)
            
            logging.info(f"Final formatted turn: '{transcript_text}'")
            asyncio.run_coroutine_threadsafe(send_client_message(websocket, {"type": "transcription", "text": transcript_text, "end_of_turn": True }), main_loop)
            llm_task = asyncio.run_coroutine_threadsafe(get_llm_response_stream(transcript_text, websocket, chat_history, user_keys), main_loop)

    def on_error(self: Type[StreamingClient], error: StreamingError): 
        logging.error(f"AssemblyAI streaming error: {error}")
        asyncio.run_coroutine_threadsafe(send_client_message(websocket, {"type": "error", "message": f"AssemblyAI Error: {error}"}), main_loop)

    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Error, on_error)

    try:
        client.connect(StreamingParameters(sample_rate=16000, format_turns=True))
        await send_client_message(websocket, {"type": "status", "message": "Connected to transcription service."})

        while True:
            message = await websocket.receive()
            if "text" in message:
                try:
                    if json.loads(message['text']).get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except (json.JSONDecodeError, TypeError): pass
            elif "bytes" in message and message['bytes']:
                client.stream(message['bytes'])
            
    except (WebSocketDisconnect, RuntimeError) as e:
        logging.info(f"Client disconnected or connection lost: {e}")
    except Exception as e:
        logging.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        if llm_task and not llm_task.done():
            llm_task.cancel()
        logging.info("Cleaning up connection resources.")
        client.disconnect()
        if websocket.client_state.name != 'DISCONNECTED':
            await websocket.close()
