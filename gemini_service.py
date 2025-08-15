import os
import logging
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logging.warning("GEMINI_API_KEY not set. AI responses will fail.")

def generate_response(prompt):
    """Generates a response using the Gemini API."""
    if not GEMINI_API_KEY:
        raise Exception("Gemini API key not configured")
    
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
        
    model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
    
    for model_name in model_names:
        try:
            logging.info(f"🤖 Trying Gemini model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text and response.text.strip():
                result = response.text.strip()
                logging.info(f"✅ Success with Gemini model: {model_name}")
                return result
        except Exception as e:
            logging.error(f"❌ Failed with {model_name}: {e}")
            continue
    
    raise Exception("All Gemini models failed to generate a response.")