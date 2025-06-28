# cohost.ai
Make cohost.ai your real-time podcast assistant and you'll never need to pause to think of what to ask next.


![License](https://img.shields.io/badge/status-beta-blue)
![LLM](https://img.shields.io/badge/LLM-meta--llama--4--scout--instruct-informational)
![Powered by](https://img.shields.io/badge/built_with-OpenAI_&_ChatGPT-green)

---

## 🚀 About Cohost

**Cohost** is an AI-powered podcast assistant designed to support podcast hosts during live or recorded sessions by automatically generating **smart and relevant follow-up questions** — in real-time.

Whether you're an experienced host or just getting started, we've all faced that awkward pause while thinking of the next thing to ask. **Cohost eliminates that gap** — helping you keep the flow natural, spontaneous, and engaging.

---

## 💡 Why Cohost?

- 🎤 **Eliminates Awkward Pauses**  
  Never struggle to come up with a follow-up question mid-conversation again.

- 🧠 **AI-Generated Follow-Ups**  
  Smart, concise, and context-aware follow-up questions powered by open-source LLM APIs.

- 🔊 **Speaker Identification**  
  You can **register your voice** in Cohost. It then uses speaker embeddings to distinguish **you (host)** from the **guest**, keeping the transcript and question generation focused and accurate.

- 👥 **Designed for 2 Speakers**  
  Currently optimized for **one host and one guest** to keep the interaction simple and controlled.

- 🤝 **Built with ChatGPT + Open Source APIs**  
  Coded with ChatGPT and powered by open-source voice processing (Vosk, PyAnnote) and language models (Meta LLaMA via Groq).

---

## 📦 Features

- 🎧 Real-time audio recording via browser
- 🔁 Automatic transcription of guest speech
- 🗣️ Host voice embedding and speaker recognition
- 💬 Dynamic follow-up question generation every few seconds
- 🖥️ Minimal and elegant UI for podcast environments
- 🛠️ Easy setup with local models and FastAPI backend

---

## 🖼️ Screenshots

### 🎙️ Speaker Registration
_Add a screenshot here (e.g., `static/speaker-registration.png`)_

### 💬 During Podcast Interface
_Add a screenshot here (e.g., `static/live-session-ui.png`)_

---

## 📁 Tech Stack

- **Frontend**: HTML + Tailwind CSS + Vanilla JS  
- **Backend**: FastAPI (Python)  
- **Voice Embedding**: `pyannote-audio`  
- **Transcription**: `Vosk` (Offline)  
- **LLM**: Meta LLaMA 4 (via Groq API)

---

## 🛠️ Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/cohost.git
   cd cohost
