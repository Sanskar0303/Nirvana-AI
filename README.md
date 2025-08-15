# Nirvana-AI 

A real-time, conversational AI assistant that lets you talk to a Large Language Model (LLM) with your voice and get a spoken response. This project is a full-stack, voice-enabled web application built with Python and JavaScript.

### 🌟 Project Overview 

This application serves as a complete example of a modern voice interface. The goal is to provide a seamless, hands-free conversational experience by intelligently handling audio input and providing natural-sounding voice responses.

Key features include:

  -->Real-time Voice Interaction: Engage in a fluid conversation with an AI.
  -->Intelligent Session Management: Start new conversations or continue old ones, with the ability to save and delete chat history.
  -->Auto-Recording (VAD): The system can automatically start and stop recording based on your voice, making the interaction feel more natural and         hands-free.
  -->Fast On-Device Transcription: In manual mode, it uses the browser's built-in `SpeechRecognition` API for near-instant transcription.
  -->Voice Responses: The AI's text replies are converted into high-quality, synthesized speech and played back automatically.
  -->Sleek UI: A clean, modern user interface with a "glassmorphism" design.

-----

### 📁 Folder Structure

The project is organized to keep the client and server components separate and easy to navigate.
.
├── .env                  # Environment variables (API keys)
├── README.md             # This file!
├── requirements.txt      # Python dependencies
├── app.py                # The Flask server application
├── static/               # Directory for static assets
│   └── image.jpeg        # The UI background image
└── templates/            # HTML templates for Flask
    └── index.html        # The main user interface

-----

### ⚙️ How to Run the Code

To get the project up and running on your local machine, follow these steps:

1.  **Clone the Repository**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Set up the Python Environment**
    Create and activate a virtual environment to manage dependencies:

    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate it (on macOS/Linux)
    source venv/bin/activate

    # Or activate it (on Windows)
    venv\Scripts\activate
    ```

    Install the necessary Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Keys**
    Create a file named **`.env`** in the root of the project. 
    This file will store your API keys securely. 
    You need to sign up for services that provide an **LLM**, a **Speech-to-Text (STT)**, and a **Text-to-Speech (TTS)**.

    Add your keys to the file:

    ```
    # Replace with your actual API keys
    LLM_API_KEY=your_llm_api_key_here
    STT_API_KEY=your_stt_api_key_here
    TTS_API_KEY=your_tts_api_key_here
    ```

4.  **Start the Server**
    Run the Flask application from your terminal:

    ```bash
    flask run
    ```

    The server will start, and you can access the application at **`http://127.0.0.1:5000`** in your web browser.

-----

### 📋 What Each File Does

  * **`app.py`**: This is the main **Flask server** file. It sets up the API endpoints that the frontend uses. It handles receiving audio files, communicating with external AI services for transcription and generation, and returning the AI's audio response.

  * **`static/`**: This folder contains all the **public, static files** that the web page needs, such as the background image. The JavaScript logic is included directly in the `index.html` file in this version of the project.

  * **`templates/`**: This folder is where Flask looks for HTML files to serve.

  * **`index.html`**: The **single-page frontend** for the entire application. It contains all the HTML structure, CSS for styling, and JavaScript logic to handle UI interactions, microphone access, and communication with the backend.

  * **`.env`**: A crucial file for **environment variables**. It keeps sensitive information like API keys separate from your code.

  * **`requirements.txt`**: This file lists all the **Python libraries** required for the project. This ensures that anyone can easily install the correct dependencies.
