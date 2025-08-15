import os
import time
import requests
import logging

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

if not ASSEMBLYAI_API_KEY:
    logging.warning("ASSEMBLYAI_API_KEY not set. Transcription will be mocked.")

def upload_to_assemblyai(filepath):
    """Uploads a local file to AssemblyAI and returns the upload_url."""
    if not ASSEMBLYAI_API_KEY:
        raise Exception("AssemblyAI API key not configured")
    
    upload_url = "https://api.assemblyai.com/v2/upload"
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    
    with open(filepath, "rb") as f:
        response = requests.post(upload_url, headers=headers, data=f, timeout=30)
    
    response.raise_for_status()
    result = response.json()
    if "upload_url" not in result:
        raise Exception("AssemblyAI upload failed - no upload URL returned")
        
    return result["upload_url"]

def transcribe_audio(filepath, timeout=60):
    """Transcribes a local file using AssemblyAI or uses a mock."""
    if not ASSEMBLYAI_API_KEY:
        logging.warning("Using mock transcription due to missing AssemblyAI key.")
        return "Hello, this is a mock transcription for a quick test."

    try:
        logging.info("⏫ Uploading to AssemblyAI...")
        upload_url = upload_to_assemblyai(filepath)
        
        logging.info("🔍 Creating transcript...")
        transcript_url = "https://api.assemblyai.com/v2/transcript"
        headers = {"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"}
        data = {"audio_url": upload_url}
        response = requests.post(transcript_url, json=data, headers=headers)
        response.raise_for_status()
        transcript_id = response.json()["id"]
        
        logging.info("⏳ Waiting for transcription...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(f"{transcript_url}/{transcript_id}", headers=headers)
            response.raise_for_status()
            status = response.json()["status"]
            
            if status == "completed":
                return response.json()["text"]
            elif status == "error":
                error_msg = response.json().get("error", "Unknown error")
                raise Exception(f"Transcription failed: {error_msg}")
            
            time.sleep(1)
        
        raise Exception("Transcription timeout")
        
    except Exception as e:
        logging.error(f"❌ Transcription error: {str(e)}")
        raise Exception(f"Transcription service failed: {e}")