import os
import json
from datetime import datetime
import logging

CHAT_HISTORY_FOLDER = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'static', 'chat_history')
os.makedirs(CHAT_HISTORY_FOLDER, exist_ok=True)
logging.info(f"Chat history folder set to: {CHAT_HISTORY_FOLDER}")

def save_chat_entry(session_id, user_message, llm_reply, audio_url=None):
    """Saves a chat entry to the history file for a given session."""
    try:
        chat_file = os.path.join(CHAT_HISTORY_FOLDER, f"chat_{session_id}.json")
        
        # Load existing history or create new
        if os.path.exists(chat_file):
            with open(chat_file, 'r') as f:
                history = json.load(f)
        else:
            history = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "messages": []
            }
        
        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "llm_reply": llm_reply,
            "audio_url": audio_url
        }
        history["messages"].append(entry)
        
        # Save updated history
        with open(chat_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        logging.info(f"Chat entry saved for session: {session_id}")
        return True
    except Exception as e:
        logging.error(f"❌ Error saving chat entry for session {session_id}: {str(e)}")
        return False

def load_chat_history(session_id):
    """Loads chat history for a session."""
    try:
        chat_file = os.path.join(CHAT_HISTORY_FOLDER, f"chat_{session_id}.json")
        if os.path.exists(chat_file):
            with open(chat_file, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        logging.error(f"❌ Error loading chat history for session {session_id}: {str(e)}")
        return None

def get_all_sessions():
    """Gets all available chat sessions."""
    try:
        sessions = []
        for filename in os.listdir(CHAT_HISTORY_FOLDER):
            if filename.startswith('chat_') and filename.endswith('.json'):
                session_id = filename[5:-5]
                chat_file = os.path.join(CHAT_HISTORY_FOLDER, filename)
                with open(chat_file, 'r') as f:
                    history = json.load(f)
                    sessions.append({
                        "session_id": session_id,
                        "created_at": history.get("created_at", ""),
                        "message_count": len(history.get("messages", [])),
                        "last_message": history["messages"][-1]["timestamp"] if history.get("messages") else None
                    })
        sessions.sort(key=lambda x: x.get("last_message") or x.get("created_at"), reverse=True)
        return sessions
    except Exception as e:
        logging.error(f"❌ Error getting sessions: {str(e)}")
        return []

def delete_chat_session(session_id):
    """Deletes a chat session file."""
    try:
        chat_file = os.path.join(CHAT_HISTORY_FOLDER, f"chat_{session_id}.json")
        if os.path.exists(chat_file):
            os.remove(chat_file)
            logging.info(f"Session {session_id} deleted successfully.")
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"❌ Failed to delete session {session_id}: {str(e)}")
        return False