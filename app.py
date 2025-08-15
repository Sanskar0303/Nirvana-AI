import os
import uuid
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__, static_folder="static", template_folder="templates")
app.logger.setLevel(logging.INFO)

# --- Service Imports ---
try:
    from services import (
        assemblyai_service, 
        murf_service, 
        gemini_service, 
        chat_history_service
    )
    logging.info("All services imported successfully.")
except ImportError as e:
    app.logger.error(f"Failed to import services: {e}. Make sure the 'services' folder and its files exist.")

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    text: str
    session_id: str | None = None

class AudioRequest(BaseModel):
    session_id: str | None = None

# --- Configuration & Folder Setup ---
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -----------------------
# Routes
# -----------------------

@app.route("/")
def index():
    """Renders the main application page."""
    return render_template("index.html")

@app.route("/static/uploads/<path:filename>")
def uploaded_file(filename):
    """Serves uploaded audio files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Chat History Routes ---
@app.route("/api/chat/sessions", methods=["GET"])
def get_chat_sessions():
    """Gets all available chat sessions."""
    sessions = chat_history_service.get_all_sessions()
    return jsonify({"sessions": sessions})

@app.route("/api/chat/history/<session_id>", methods=["GET"])
def get_chat_history(session_id):
    """Gets chat history for a specific session."""
    history = chat_history_service.load_chat_history(session_id)
    if history:
        return jsonify(history)
    else:
        return jsonify({"error": "Session not found"}), 404

@app.route("/api/chat/delete/<session_id>", methods=["DELETE"])
def delete_chat_session(session_id):
    """Deletes a chat session."""
    success = chat_history_service.delete_chat_session(session_id)
    if success:
        return jsonify({"success": True, "message": "Session deleted"})
    else:
        return jsonify({"error": "Session not found"}), 404

# --- Direct Q&A Route (Text-based) ---
@app.route("/qa/answer", methods=["POST"])
def qa_answer():
    """Direct text-based Q&A without audio processing."""
    try:
        data = ChatRequest.model_validate(request.get_json())
        question = data.text.strip()
        session_id = data.session_id or str(uuid.uuid4())
        
        app.logger.info(f"Direct Q&A request received. Session ID: {session_id}")
        
        # Get AI response
        llm_reply = gemini_service.generate_response(question)
        
        # Generate TTS for the response
        audio_url = None
        try:
            app.logger.info("Attempting to generate TTS with Murf...")
            tts_audio_url = murf_service.get_murf_audio(llm_reply)
            
            # Download and save Murf audio
            audio_url = murf_service.download_audio(tts_audio_url, app.config['UPLOAD_FOLDER'])
            app.logger.info("Successfully generated and saved TTS audio.")
        except Exception as tts_error:
            app.logger.warning(f"Murf TTS failed: {tts_error}. Attempting fallback TTS.")
            # Fallback to local gTTS
            fallback_response = murf_service.fallback_tts(llm_reply, app.config['UPLOAD_FOLDER'])
            audio_url = fallback_response['audio_url']
            app.logger.info("Used fallback TTS successfully.")
            
        # Save to chat history
        chat_history_service.save_chat_entry(session_id, question, llm_reply, audio_url)
        
        return jsonify({
            "transcript": question,
            "llm_reply": llm_reply,
            "audio_url": audio_url,
            "session_id": session_id
        })
        
    except ValidationError as e:
        app.logger.error(f"Validation error in /qa/answer: {e}")
        return jsonify({"error": f"Invalid request data: {e}"}), 400
    except Exception as e:
        app.logger.error(f"Error in /qa/answer endpoint: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# --- LLM Pipeline Route (Audio-based) ---
@app.route("/llm/query", methods=["POST"])
def llm_query_audio():
    """Processes an audio file through the full AI pipeline."""
    try:
        # Pydantic validation for form data is not as straightforward, so we'll do a check
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        uploaded_file = request.files["audio"]
        if uploaded_file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        session_id = request.form.get('session_id', str(uuid.uuid4()))
        
        # Save uploaded audio temporarily
        tmp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}.webm")
        uploaded_file.save(tmp_path)
        app.logger.info(f"Audio file saved temporarily to {tmp_path}")

        # Step 1: Transcribe audio
        transcript_text = assemblyai_service.transcribe_audio(tmp_path)
        app.logger.info(f"Audio transcribed: {transcript_text[:50]}...")

        if not transcript_text:
            return jsonify({"error": "Transcription failed or returned no text."}), 400

        # Step 2: Get AI response
        llm_reply = gemini_service.generate_response(transcript_text)
        app.logger.info(f"Gemini LLM replied: {llm_reply[:50]}...")

        # Step 3: Generate TTS and save audio
        audio_url = None
        try:
            tts_audio_url = murf_service.get_murf_audio(llm_reply)
            audio_url = murf_service.download_audio(tts_audio_url, app.config['UPLOAD_FOLDER'])
            app.logger.info("Successfully generated and saved Murf audio.")
        except Exception as tts_error:
            app.logger.warning(f"Murf TTS failed: {tts_error}. Using fallback TTS.")
            fallback_response = murf_service.fallback_tts(llm_reply, app.config['UPLOAD_FOLDER'])
            audio_url = fallback_response['audio_url']

        # Step 4: Save to chat history
        chat_history_service.save_chat_entry(session_id, transcript_text, llm_reply, audio_url)
        
        return jsonify({
            "transcript": transcript_text,
            "llm_reply": llm_reply,
            "audio_url": audio_url,
            "session_id": session_id
        })

    except Exception as e:
        app.logger.error(f"Error in LLM query pipeline: {e}")
        return jsonify({"error": f"Pipeline failed: {str(e)}"}), 500
    finally:
        # Clean up temporary audio file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            app.logger.info(f"Cleaned up temporary file: {tmp_path}")


# -----------------------
# Entry Point
# -----------------------
if __name__ == "__main__":
    app.logger.info("🚀 Starting AI Voice Agent.")
    app.run(host="0.0.0.0", port=os.getenv("PORT", 5016), debug=True)