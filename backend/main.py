# uvicorn main:app  # uvicorn main:app --reload
# main imports
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai
# Custom function imports
from functions.openai_requests import convert_audio_to_text, get_gpt_response
from functions.database import update_conversation_history



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
    audio_file = open("data/voice.mp3", "rb")
    transcription = convert_audio_to_text(audio_file)
    # guard message decoded
    if transcription is None:
        raise HTTPException(status_code=500, detail="Error decoding audio")
    response = get_gpt_response(transcription)
    update_conversation_history(transcription, response)
    print(response)
    return "Done"