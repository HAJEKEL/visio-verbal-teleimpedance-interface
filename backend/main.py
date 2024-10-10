# uvicorn main:app  # uvicorn main:app --reload
# main imports
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config

# Custom function imports
from functions.vosk_stt import speech_to_text
from functions.openai_response_tts import get_gpt_response, text_to_speech
from functions.database import update_conversation_history, reset_conversation_history



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

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def check_health():
    return {"status": "ok"}

@app.get("/reset")
async def reset():
    return reset_conversation_history()


@app.get("/get_audio")
async def get_audio():
    # Get saved audio file
    audio_file = "data/voice.wav"
    transcription = speech_to_text(audio_file)
    print(transcription)
    # guard message decoded
    if transcription is None:
        raise HTTPException(status_code=500, detail="Error decoding audio")
    response = get_gpt_response(transcription)
    print(response)
    if response is None:
        raise HTTPException(status_code=500, detail="Error fetching gpt response")
    update_conversation_history(transcription, response)
    text_to_speech(response)
    # if audio is None:
    #     raise HTTPException(status_code=500, detail="Error generating audio response")
    # return "Done"

from fastapi import UploadFile, File, HTTPException
import os

@app.post("/post_audio/")
async def post_audio(file: UploadFile = File(...)):
    try:
        # Define a path to save the uploaded audio file
        file_path = f"data/{file.filename}"

        # Save the uploaded file to disk
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Pass the file path to the speech_to_text function
        transcription = speech_to_text(file_path)
        print(transcription)

        # Guard clause for message decoding
        if transcription is None:
            raise HTTPException(status_code=500, detail="Error decoding audio")

        # Get GPT response
        response = get_gpt_response(transcription)
        print(response)

        # Guard clause for GPT response
        if response is None:
            raise HTTPException(status_code=500, detail="Error fetching GPT response")

        # Update conversation history and generate voice response
        update_conversation_history(transcription, response)
        text_to_speech(response)

        return {"message": "Audio processed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up by removing the saved file after processing
        if os.path.exists(file_path):
            os.remove(file_path)
