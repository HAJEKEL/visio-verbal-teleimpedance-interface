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
    "https://summary-sunbird-dashing.ngrok-free.app"
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
async def post_audio(file: UploadFile = File(...)):
    try:
        # Define a path to save the uploaded audio file
        original_file_path = f"data/{file.filename}"
        converted_file_path = f"data/converted_{file.filename}"

        # Save the uploaded file to disk
        with open(original_file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Use ffmpeg to convert the audio to the required format
        ffmpeg.input(original_file_path).output(
            converted_file_path, ac=1, ar=16000
        ).run()

        # Pass the converted file to the speech_to_text function
        transcription = speech_to_text(converted_file_path)
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
        # Generate the audio from text
        audio_file_path = text_to_speech(response)

        # Guard: Ensure output
        if not audio_file_path or not os.path.exists(audio_file_path):
            raise HTTPException(status_code=400, detail="Failed to generate audio")

        # Create a generator that yields the audio file chunks
        def iterfile():
            with open(audio_file_path, mode="rb") as file_like:
                yield from file_like

        # Return the audio file as a stream
        return StreamingResponse(iterfile(), media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up: remove the saved file
        # if os.path.exists(audio_file_path):
        #     os.remove(audio_file_path)
        # Clean up: remove the saved files
        if os.path.exists(original_file_path):
            os.remove(original_file_path)
        if os.path.exists(converted_file_path):
            os.remove(converted_file_path)

@app.post("/capture_data")
async def capture_data(image_url: str):
    try:
        # Capture audio transcription
        original_file_path = f"data/{file.filename}"
        converted_file_path = f"data/converted_{file.filename}"
        with open(original_file_path, "wb") as buffer:
            buffer.write(await file.read())
        ffmpeg.input(original_file_path).output(converted_file_path, ac=1, ar=16000).run()
        transcription = speech_to_text(converted_file_path)
        # Send both transcription and image to OpenAI API
        response = vlm(transcription, image_url)

        return {"openai_response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Generate a unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid4()}.{file_extension}"
        file_path = f"static/images/{unique_filename}"

        # Save the file to the static/images folder
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Generate the file URL using your ngrok domain
        file_url = f"https://summary-sunbird-dashing.ngrok-free.app/static/images/{unique_filename}"

        # Call /capture_data endpoint with the image URL
        response = requests.post("http://localhost:8000/capture_data/", json={"image_url": file_url})

        # Return the OpenAI response
        return JSONResponse(content=response.json())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
