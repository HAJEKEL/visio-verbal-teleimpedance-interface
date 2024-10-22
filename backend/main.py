# uvicorn main:app  # uvicorn main:app --reload
# audio format: wav
import ffmpeg
# 
import os

# main imports
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config

# Custom function imports
from functions.vosk_stt import speech_to_text
from functions.openai_response_tts import get_gpt_response, text_to_speech
from functions.database import update_conversation_history, reset_conversation_history
from functions.tts_play_directly import text_to_speech_play_directly
from functions.openai_vlm import get_gpt_response_vlm
from functions.database import update_conversation_history_vlm
# Make a static folder to send images to openai
from fastapi.staticfiles import StaticFiles
# For unique file names
from uuid import uuid4



# Initiate app
app = FastAPI()
# CORS origins that are allowed to connect to this server
origins = [
    "http://localhost:5173", # React dev server
    "http://localhost:5174", # React dev server second
    "http://localhost:4173", # React deploy server
    "http://localhost:4174", # React deploy server second
    "http://localhost:3000",
    "http://127.0.0.1:5174", # Add 127.0.0.1 for browser's localhost interpretation
    "http://127.0.0.1:5173",  # Add 127.0.0.1 as another dev server
    "https://summary-sunbird-dashing.ngrok-free.app",
    "https://fa04-188-88-134-208.ngrok-free.app"
    ] # General frontend application server

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the "static" folder
app.mount("/static", StaticFiles(directory="static"), name="static")


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
    text_to_speech_play_directly(response)
    # if audio is None:
    #     raise HTTPException(status_code=500, detail="Error generating audio response")
    # return "Done"


@app.post("/post_audio")
async def post_audio(file: UploadFile = File(...), image_url: str = None):
    try:
        # Image URL will now correctly be included from the form
        print(f"Received image URL: {image_url}")

        # Audio processing code remains the same
        original_file_path = f"data/{file.filename}"
        converted_file_path = f"data/converted_{file.filename}"

        with open(original_file_path, "wb") as buffer:
            buffer.write(await file.read())

        ffmpeg.input(original_file_path).output(converted_file_path, ac=1, ar=16000).global_args('-loglevel', 'error', '-hide_banner').run()


        transcription = speech_to_text(converted_file_path)
        if transcription is None:
            raise HTTPException(status_code=500, detail="Error decoding audio")

        # Use the multimodal response if image_url exists
        if image_url:
            response = get_gpt_response_vlm(transcription, image_url)
        else:
            response = get_gpt_response(transcription)

        if response is None:
            raise HTTPException(status_code=500, detail="Error fetching GPT response")

        # Update conversation history with or without image
        if image_url:
            update_conversation_history_vlm(transcription, image_url, response)
        else:
            update_conversation_history(transcription, response)

        audio_file_path = text_to_speech(response)
        if not audio_file_path or not os.path.exists(audio_file_path):
            raise HTTPException(status_code=400, detail="Failed to generate audio")

        def iterfile():
            with open(audio_file_path, mode="rb") as file_like:
                yield from file_like

        return StreamingResponse(iterfile(), media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(original_file_path):
            os.remove(original_file_path)
        if os.path.exists(converted_file_path):
            os.remove(converted_file_path)


@app.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        if not os.path.exists("static/images"):
            os.makedirs("static/images")
        # Generate a unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid4()}.{file_extension}"
        file_path = f"static/images/{unique_filename}"

        # Save the file to the static/images folder
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Generate the file URL using your ngrok domain
        file_url = f"https://summary-sunbird-dashing.ngrok-free.app/static/images/{unique_filename}"
        return file_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


