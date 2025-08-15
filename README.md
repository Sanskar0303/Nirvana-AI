# Nirvana-AI 🎤🤖

A real-time, conversational AI assistant that lets you talk to a Large Language Model (LLM) with your voice and get a spoken response. This is a full-stack, voice-enabled web application built with Python and JavaScript.

🚀 Key Features
This application serves as a complete example of a modern voice interface, providing a seamless, hands-free conversational experience.

Real-time Voice Interaction: Engage in a fluid conversation with an AI.

Intelligent Session Management: Start new conversations or continue old ones, with the ability to save and delete chat history.

Auto-Recording (VAD): The system can automatically start and stop recording based on your voice, making the interaction feel more natural and hands-free.

Fast Transcription: In manual mode, it uses the browser's built-in SpeechRecognition API for near-instant transcription.

Voice Responses: The AI's text replies are converted into high-quality, synthesized speech and played back automatically.

Sleek UI: A clean, modern user interface with a "glassmorphism" design.

📁 Project Structure
The project is organized to keep the client and server components separate and easy to navigate.

.
├── .env                # Environment variables (API keys)
├── README.md           # This file!
├── requirements.txt    # Python dependencies
├── app.py              # The Flask server application
├── static/             # Directory for static assets
│   └── image.jpeg      # The UI background image
├── templates/          # HTML templates for Flask
│   └── index.html      # The main user interface
└── services/           # Backend services
    ├── __init__.py     # Makes the directory a Python package
    ├── llm_service.py  # Handles LLM interactions
    ├── stt_service.py  # Handles Speech-to-Text
    └── tts_service.py  # Handles Text-to-Speech
    
⚙️ How to Run the Code
To get the project up and running on your local machine, follow these steps:

1. Clone the Repository
Open your terminal and run the following command to clone the project:

Bash

git clone <repository_url>
cd <repository_directory>
2. Set up the Python Environment
It's highly recommended to use a virtual environment to manage dependencies.

Bash

# Create the virtual environment
python -m venv venv

# Activate it (on macOS/Linux)
source venv/bin/activate

# Or activate it (on Windows)
venv\Scripts\activate
Next, install the necessary Python packages:

Bash

pip install -r requirements.txt
3. Configure API Keys
Create a file named .env in the root of the project to store your API keys securely. You need to sign up for services that provide an LLM, a Speech-to-Text (STT), and a Text-to-Speech (TTS).

# Replace with your actual API keys
GEMINI_API_KEY=your_gemini_api_key_here
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
MURF_API_KEY=your_murf_api_key_here
4. Start the Server
Run the Flask application from your terminal:

Bash

flask run
The server will start, and you can access the application at http://127.0.0.1:5000 in your web browser.

📋 File Descriptions
app.py: The main Flask server file. It sets up the API endpoints that the frontend uses and connects to the backend services.

static/: This folder contains all the public, static files that the web page needs, such as the background image.

templates/: Flask looks for HTML files to serve in this folder.

index.html: The single-page frontend for the entire application. It contains all the HTML, CSS, and JavaScript logic to handle UI interactions and microphone access.

.env: A crucial file for environment variables. It keeps sensitive information like API keys separate from your code.

requirements.txt: This file lists all the Python libraries required for the project.
