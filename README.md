# Nirvana AI 🎙️  
**30 Days of AI Voice Agents | Day 29 - Final Documentation**

---

## 📌 Overview
Nirvana AI is an **AI-powered voice agent** built as part of the **30 Days of AI Voice Agents Challenge**.  
The project explores **real-time transcription, text-to-speech, conversational intelligence, and compliance-focused document processing** using **AssemblyAI** and **Murf AI**.  

Over 29 days, Nirvana AI evolved from a simple echo bot into a **multi-featured intelligent assistant** with advanced document intelligence, voice generation, and modular backend support.

---

## 🚀 Features Implemented
- 🎧 **Real-time Audio Transcription** (AssemblyAI)  
- 🎤 **High-quality TTS (Text-to-Speech)** (Murf AI)  
- 🪞 **Echo Bot** – listens and instantly replies with AI voice  
- 🖥️ **Frontend UI** for mic input & playback  
- 🔗 **Backend Integration** with Flask & FastAPI  
- 🎙️ **Custom Voice Selection** from Murf library  
- ⚡ **Seamless Audio Streaming** with WebSockets  
- 📄 **JSON + .docx Output Generation**  
- ✅ **ADGM-Compliant Document Intelligence Mode**  
  - Legal red flag detection  
  - Compliance checklist verification  
  - Smart document parsing  

---

## 🛠️ Tech Stack
- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Flask + FastAPI  
- **APIs:** AssemblyAI (STT), Murf AI (TTS)  
- **Libraries:** Websockets, asyncio, JSON, docx  

---

## 📂 Project Structure
nirvana-ai/
│── static/ # Frontend assets (HTML, JS, CSS)
│── templates/ # Jinja2 templates
│── app.py # Flask app
│── main.py # FastAPI app
│── requirements.txt
│── README.md


---

## 📅 Journey: Day 1 → Day 29

### 🔹 Week 1: Foundations
- **Day 1:** Setup project structure, basic Flask app  
- **Day 2:** Integrated Murf AI for basic text-to-speech  
- **Day 3:** Added frontend microphone input  
- **Day 4:** Connected AssemblyAI for speech-to-text  
- **Day 5:** Built simple Echo Bot (listen → transcribe → reply)  
- **Day 6:** Polished Echo Bot responses with Murf voices  
- **Day 7:** Completed Echo Bot loop (record → transcribe → TTS playback)  

### 🔹 Week 2: Frontend & Streaming
- **Day 8:** Improved frontend UI (HTML, CSS, JS)  
- **Day 9:** Added WebSocket connection for real-time audio streaming  
- **Day 10:** Implemented continuous transcription logging  
- **Day 11:** Added replay button for past transcriptions  
- **Day 12:** Optimized audio playback buffer  
- **Day 13:** Enabled voice selection from Murf library  
- **Day 14:** Cleaned frontend for smoother UX  

### 🔹 Week 3: Backend Expansion
- **Day 15:** Started FastAPI integration alongside Flask  
- **Day 16:** Created modular API endpoints  
- **Day 17:** Added async streaming with asyncio  
- **Day 18:** Refactored backend for low latency  
- **Day 19:** Introduced simple session handling  
- **Day 20:** Improved error handling and logging  
- **Day 21:** Synced Flask + FastAPI routes for dual support  

### 🔹 Week 4: Intelligence Layer
- **Day 22:** Added structured JSON output for conversations  
- **Day 23:** Exported transcripts into `.docx` format  
- **Day 24:** Added support for multiple conversations per session  
- **Day 25:** Designed basic compliance checklist feature  
- **Day 26:** Integrated ADGM document rules (templates & parsing)  
- **Day 27:** Implemented legal red flag detection system  
- **Day 28:** Enhanced docx + JSON compliance report generation  
- **Day 29:** Final cleanup, documentation, and README preparation 🚀  

---

## 🎯 Key Learnings
- Handling **real-time audio streaming** with low latency  
- Using **Murf AI + AssemblyAI** effectively for voice agents  
- Structuring **multi-backend architecture (Flask + FastAPI)**  
- Building **compliance-focused document intelligence**  
- Writing clean, modular code for scalability  

---

## 📢 Next Steps
- ☁️ Deploy Nirvana AI to cloud hosting (Heroku / Render / Railway)  
- 🧠 Add RAG-based knowledge answering using custom docs  
- 🌍 Extend to multilingual voice agents  
- 📦 Package as a plug-and-play AI Voice SDK  

---

## 👩‍💻 Author
**Sanskar Soni**  

---

✨ *Day 29 completed!* Just one more step to the **grand finale of Nirvana AI** 🚀
