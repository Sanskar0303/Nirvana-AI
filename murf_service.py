import os
import uuid
import requests
import logging
from gtts import gTTS

MURF_API_KEY = os.getenv("MURF_API_KEY")

if not MURF_API_KEY:
    logging.warning("MURF_API_KEY not set. Murf TTS will be skipped.")

def get_murf_audio(text, voice_id="en-US-natalie", output_format="MP3"):
    """Generates TTS audio file URL using Murf API."""
    if not MURF_API_KEY:
        raise Exception("Murf API key not configured")
    
    url = "https://api.murf.ai/v1/speech/generate"
    
    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text.strip(),
        "voiceId": voice_id,
        "outputFormat": output_format
    }
    
    response = requests.post(url, json=data, headers=headers, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    audio_url = result.get("audioFile")
    if not audio_url:
        raise Exception("Murf returned no audio URL")
    
    return audio_url

def download_audio(url, download_folder):
    """Downloads an audio file and returns its local path."""
    if not url:
        return None

    audio_response = requests.get(url, timeout=30)
    audio_response.raise_for_status()

    filename = f"tts_response_{uuid.uuid4().hex[:8]}.mp3"
    filepath = os.path.join(download_folder, filename)
    
    with open(filepath, "wb") as f:
        f.write(audio_response.content)
    
    return f"/static/uploads/{filename}"

def fallback_tts(text, download_folder):
    """Generates local TTS audio using gTTS."""
    try:
        tts = gTTS(text=text, lang='en')
        filename = f"fallback_tts_{uuid.uuid4().hex[:8]}.mp3"
        out_path = os.path.join(download_folder, filename)
        tts.save(out_path)
        logging.info(f"✅ gTTS fallback audio saved: {out_path}")
        return {
            "audio_url": f"/static/uploads/{filename}",
            "message": "Generated with gTTS fallback"
        }
    except Exception as e:
        logging.error(f"⚠️ gTTS fallback failed: {e}")
        return {
            "audio_url": None,
            "message": "TTS generation failed entirely."
        }