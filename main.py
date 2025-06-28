import os
import json
import torch
import numpy as np
import subprocess
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pyannote.audio import Inference
from scipy.spatial.distance import cosine
from pydantic import BaseModel
from typing import List

from transcribe import transcribe_with_vosk
from llm_interface import LLMInterface
from speaker_identifier import VoiceIdentifier
from agent import PodcastAgent

# Set API Key
os.environ["GROQ_API_KEY"] = "<your_api_key>"

# File paths
CONTEXT_FILE = "podcast_context.json"
EMBEDDING_FILE = "voice_embeddings.json"

# Components
identifier = VoiceIdentifier()
llm = LLMInterface()

# Globals
conversation_buffer = []
podcast_context = {}
inference = Inference("pyannote/embedding", use_auth_token=None, device=torch.device("cpu"))
agent = PodcastAgent(context=podcast_context, llm_interface=llm)

# FastAPI app
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def load_data():
    global podcast_context
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r") as f:
            podcast_context.update(json.load(f))
        print("[🔄] Loaded podcast context.")
    if os.path.exists(EMBEDDING_FILE):
        print("[🔄] Loaded existing speaker embeddings.")


def transcriber(audio_bytes):
    import tempfile
    import soundfile as sf

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_webm:
        temp_webm.write(audio_bytes)
        temp_webm.flush()

    temp_wav = tempfile.mktemp(suffix=".wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", temp_webm.name,
        "-ar", "16000", "-ac", "1", temp_wav
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    data, samplerate = sf.read(temp_wav)
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    if data.dtype != np.int16:
        data = (data * 32767).astype(np.int16)

    os.remove(temp_webm.name)
    os.remove(temp_wav)

    return transcribe_with_vosk(data, samplerate)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    return templates.TemplateResponse("setup.html", {"request": request})


@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})


@app.get("/transcribe", response_class=HTMLResponse)
async def transcribe_page(request: Request):
    return templates.TemplateResponse("transcribe.html", {"request": request})


@app.get("/setup_context/")
async def get_context():
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r") as f:
            return json.load(f)
    return {}


@app.post("/upload/")
async def upload_speaker_voice(file: UploadFile = File(...)):
    temp_input = "temp_host.webm"
    temp_wav = "temp_host.wav"

    with open(temp_input, "wb") as f:
        f.write(await file.read())

    subprocess.run(["ffmpeg", "-y", "-i", temp_input, "-ar", "16000", "-ac", "1", temp_wav],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    embedding = inference(temp_wav).data.mean(axis=0).tolist()

    if os.path.exists(EMBEDDING_FILE):
        try:
            with open(EMBEDDING_FILE, "r") as f:
                speakers = json.load(f)
        except json.JSONDecodeError:
            speakers = []
    else:
        speakers = []

    speakers = [s for s in speakers if s.get("speaker") != "Host"]
    speakers.append({"speaker": "Host", "embedding": embedding})

    with open(EMBEDDING_FILE, "w") as f:
        json.dump(speakers, f, indent=2)

    os.remove(temp_input)
    os.remove(temp_wav)

    print(f"[✅] Host embedding saved: {EMBEDDING_FILE}")
    return JSONResponse(content={"message": "✅ Host voice registered!"})


@app.post("/recording/")
async def process_audio(file: UploadFile = File(...)):
    global conversation_buffer
    audio_data = await file.read()
    transcript = transcriber(audio_data)
    speaker = identifier.identify_speaker(audio_data)

    if speaker == "Unknown":
        speaker = "Guest"

    entry = {"speaker": speaker, "text": transcript}
    conversation_buffer.append(entry)

    print(f"[🧠] Identified speaker: {speaker}")
    print(f"[📝] Transcript: {transcript}")
    print(f"[📥] Added to conversation_buffer: {entry}")
    print(f"[📦] Buffer now has {len(conversation_buffer)} entries.")

    return {"speaker": speaker, "text": transcript}


@app.get("/followups/")
async def get_followups():
    global conversation_buffer
    print(f"[🔎] Checking conversation buffer with {len(conversation_buffer)} entries.")
    if not podcast_context or not conversation_buffer:
        return {"questions": []}

    valid_transcript = [t for t in conversation_buffer if len(t.get("text", "")) > 5]
    if not valid_transcript:
        return {"questions": []}

    questions = llm.generate_followups(podcast_context, valid_transcript)
    return {"questions": questions}


class ContextInput(BaseModel):
    guest_name: str
    guest_bio: str
    podcast_goal: str
    podcast_topic: str
    starter_questions: List[str]


@app.post("/setup_context/")
async def setup_context(data: ContextInput):
    context_dict = data.model_dump()

    with open(CONTEXT_FILE, "w") as f:
        json.dump(context_dict, f, indent=2)

    podcast_context.update(context_dict)
    agent.context = podcast_context
    print(f"[✅] Saved podcast context to: {os.path.abspath(CONTEXT_FILE)}")

    return {"message": "Podcast context saved successfully", "context": podcast_context}
