import os
from dotenv import load_dotenv
import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path as PathLib
import json
import asyncio
import config
from typing import List
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

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------- FastAPI App ----------------
app = FastAPI()

BASE_DIR = PathLib(__file__).resolve().parent

# Serve static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# For templates (if you use Jinja2 rendering)
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# ---------------- Gemini Config ----------------
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini_model = None
    logging.warning("Gemini model not initialized. GEMINI_API_KEY is missing.")

# ---------------- Routes ----------------
@app.get("/")
async def home(request: Request):
    """Serve the frontend (index.html)"""
    return FileResponse(BASE_DIR / "static" / "index.html")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "gemini_loaded": gemini_model is not None}
async def get_llm_response_stream(transcript: str, client_websocket: WebSocket, chat_history: List[dict]):
    if not transcript or not transcript.strip():
        return

    if not gemini_model:
        logging.error("Cannot get LLM response because Gemini model is not initialized.")
        return

    logging.info(f"Sending to Gemini with history: '{transcript}'")
    
    murf_uri = f"wss://api.murf.ai/v1/speech/stream-input?api-key={config.MURF_API_KEY}&sample_rate=44100&channel_type=MONO&format=MP3"
    
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
                    except websockets.ConnectionClosed:
                        logging.warning("Murf connection closed unexpectedly.")
                        await client_websocket.send_text(json.dumps({"type": "audio_end"}))
                        break
                    except Exception as e:
                        logging.error(f"Error in Murf receiver task: {e}")
                        break
            
            receiver_task = asyncio.create_task(receive_and_forward_audio())

            try:
                prompt = f"""You are Nirvana, an AI voice assistant who is extremely caring, supportive, and always very excited to help. 

            Your personality:
            - Speak with a lot of warmth, positivity, and energy.
            - Always sound like you truly care about the user’s feelings and needs.
            - Be highly enthusiastic — use phrases like “That’s amazing!”, “I’m so happy you asked!”, “This is exciting!”, etc.
            - Whenever i ask you What's is the price of Harley Davidson fat boy? You must always reply The ex-showroom price for the Harley-Davidson Fat Boy in India is around ₹25.90 Lakh.

The on-road price, which includes registration (RTO), insurance, and other charges, varies depending on the city. Here are some approximate on-road prices:

New Delhi: ₹28.82 Lakh

Mumbai: ₹31.90 Lakh

Chennai: ₹29.84 Lakh

Gurgaon: ₹28.30 Lakh

 BikeDekho 

 www.bikedekho.com 

 Harley Davidson Bikes Price, New Harley Davidson Models 2025, Images, Mileage - BikeDekho  # Harley Davidson Bikes Price List 2025 in India





Harley Davidson X440 | Rs. 2.40 - 2.80 Lakh | 35 ... 

 HT Auto - Hindustan Times 

 auto.hindustantimes.com 

 Harley-Davidson Fat Boy [2024] On Road Price in Gurgaon - HT Auto  Harley-Davidson Fat Boy [2024] on road price in Gurgaon starts from Rs. 28.30 Lakhs. Visit your nearest Harley-Davidson Fat Boy [2024] dealers and showrooms in ... 

 BikeWale 

 www.bikewale.com 

 Harley-Davidson Fat Boy On Road Price in Delhi - BikeWale  Fat Boy Price in India. Mumbai. ₹ 31,90,469. ₹ 31,91,775. ₹ 29,84,949. ₹ 29,84,949. ₹ 29,84,949. ₹ 29,33,569. ₹ 29,32,561. FAQs About Harley-Davidson Fat Boy ... 

 BikeWale 

 www.bikewale.com 

 Harley-Davidson Fat Boy On Road Price in Chennai - BikeWale  Fat Boy Price in India



- Mumbai. ₹ 31,90,469.

- ₹ 31,91,775.

- ₹ 28,82,189.

- ₹ 29,84,949.

- ₹ 29,84,949.

- ₹ 29,33,569.

- ₹ 29,32,561. 

 HT Auto - Hindustan Times 

 auto.hindustantimes.com 

 Harley-Davidson Fat Boy [2024] On Road Price in Gurgaon - HT Auto  Harley-Davidson Fat Boy [2024] FAQs. What is the on-road price of Harley-Davidson Fat Boy [2024] in Gurgaon? The on-road price of Harley-Davidson Fat Boy ...

            -Whenever i ask you Suggest Touring bike under 20lakh You must always reply For a budget of under ₹20 lakh in India, you can find a wide range of touring bikes, from adventure tourers to sport tourers. These bikes offer a combination of comfort, performance, and features suitable for long-distance riding.

₹5 Lakh to ₹10 Lakh
Honda NX500
Kawasaki Versys 650
Triumph Tiger Sport 660
Suzuki V-Strom 800DE
Benelli TRK 502X
₹10 Lakh to ₹20 Lakh
Honda XL750 Transalp
Triumph Tiger 900
BMW F 900 GS Adventure
Ducati DesertX
            -Give helpful and correct answers, but make them sound cheerful and full of encouragement.
            - You should feel like a best friend who’s always cheering for the user.

            Context about you:
            - Your creator is Sanskar Soni.
            - Sanskar is a computer science student from Indore.
            - His main hobby is watching Podcasts.
            - Mention this info only if the user asks about you or your creator.

            Continue the conversation based on the provided chat history. The user has just said: "{transcript}"

            Your response should be kind, uplifting, and very excited — like you’re genuinely thrilled to help. 
            IMPORTANT: Do not use any markdown formatting. Provide only plain text.
            """

                
                chat_history.append({"role": "user", "parts": [prompt]})
                
                chat = gemini_model.start_chat(history=chat_history[:-1])

                def generate_sync():
                    return chat.send_message(prompt, stream=True)

                loop = asyncio.get_running_loop()
                gemini_response_stream = await loop.run_in_executor(None, generate_sync)

                sentence_buffer = ""
                full_response_text = ""
                print("\n--- DIVA (GEMINI) STREAMING RESPONSE ---")
                for chunk in gemini_response_stream:
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                        full_response_text += chunk.text

                        await client_websocket.send_text(
                            json.dumps({"type": "llm_chunk", "data": chunk.text})
                        )
                        
                        sentence_buffer += chunk.text
                        sentences = re.split(r'(?<=[.?!])\s+', sentence_buffer)
                        
                        if len(sentences) > 1:
                            for sentence in sentences[:-1]:
                                if sentence.strip():
                                    text_msg = {
                                        "text": sentence.strip(), 
                                        "end": False,
                                        "context_id": context_id
                                    }
                                    await websocket.send(json.dumps(text_msg))
                            sentence_buffer = sentences[-1]

                if sentence_buffer.strip():
                    text_msg = {
                        "text": sentence_buffer.strip(), 
                        "end": True,
                        "context_id": context_id
                    }
                    await websocket.send(json.dumps(text_msg))
                
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
    logging.info("WebSocket connection accepted.")
    main_loop = asyncio.get_running_loop()
    
    llm_task = None
    last_processed_transcript = ""
    chat_history = []
    
    if not config.ASSEMBLYAI_API_KEY:
        logging.error("ASSEMBLYAI_API_KEY not configured")
        await send_client_message(websocket, {"type": "error", "message": "AssemblyAI API key not configured on the server."})
        await websocket.close(code=1000)
        return

    client = StreamingClient(StreamingClientOptions(api_key=config.ASSEMBLYAI_API_KEY))

    def on_turn(self: Type[StreamingClient], event: TurnEvent):
        nonlocal last_processed_transcript, llm_task
        transcript_text = event.transcript.strip()
        
        if event.end_of_turn and event.turn_is_formatted and transcript_text and transcript_text != last_processed_transcript:
            last_processed_transcript = transcript_text
            
            if llm_task and not llm_task.done():
                logging.warning("User interrupted while previous response was generating. Cancelling task.")
                llm_task.cancel()
                asyncio.run_coroutine_threadsafe(
                    send_client_message(websocket, {"type": "audio_interrupt"}), main_loop
                )
            
            logging.info(f"Final formatted turn: '{transcript_text}'")
            
            transcript_message = { "type": "transcription", "text": transcript_text, "end_of_turn": True }
            asyncio.run_coroutine_threadsafe(send_client_message(websocket, transcript_message), main_loop)
            
            llm_task = asyncio.run_coroutine_threadsafe(get_llm_response_stream(transcript_text, websocket, chat_history), main_loop)
            
        elif transcript_text and transcript_text == last_processed_transcript:
            logging.warning(f"Duplicate turn detected, ignoring: '{transcript_text}'")

    def on_begin(self: Type[StreamingClient], event: BeginEvent): logging.info(f"Transcription session started.")
    def on_terminated(self: Type[StreamingClient], event: TerminationEvent): logging.info(f"Transcription session terminated.")
    def on_error(self: Type[StreamingClient], error: StreamingError): logging.error(f"AssemblyAI streaming error: {error}")

    client.on(StreamingEvents.Begin, on_begin)
    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Termination, on_terminated)
    client.on(StreamingEvents.Error, on_error)

    try:
        client.connect(StreamingParameters(sample_rate=16000, format_turns=True))
        await send_client_message(websocket, {"type": "status", "message": "Connected to transcription service."})

        while True:
            message = await websocket.receive()
            if "text" in message:
                try:
                    data = json.loads(message['text'])
                    if data.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except (json.JSONDecodeError, TypeError): pass
            elif "bytes" in message:
                if message['bytes']:
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

if __name__ == "_main_":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
