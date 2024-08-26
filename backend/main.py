# uvicorn main:app  # uvicorn main:app --reload
# main imports
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai

# Custom function imports
from functions.openai_requests import convert_audio_to_text


# Initiate app
app = FastAPI()
# CORS origins that are allowed to connect to this server
origins = [
    "http://localhost:5173", # React dev server
    "http://localhost:5174", # React dev server second
    "http://localhost:4173", # React deploy server
    "http://localhost:4174", # React deploy server second
    "http://localhost:3000"] # General frontend application server

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def check_health():
    return {"status": "ok"}

@app.get("/get_audio")
async def get_audio():
    # Get saved audio file
    audio_file = open("voice.mp3", "rb")
    decoded_audio = convert_audio_to_text(audio_file)
    print("decoded_audio", decoded_audio)
    return "Done"