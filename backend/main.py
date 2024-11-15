# uvicorn main:app  # uvicorn main:app --reload
# audio format: wav
import ffmpeg
import os
import numpy as np
import matplotlib.pyplot as plt
import requests
import json

os.environ["VOSK_LOG_LEVEL"] = "-1"  # Disable all Vosk logs

# main imports
from fastapi import BackgroundTasks
from fastapi.responses import FileResponse
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
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
from functions.stiffness_extractor import extract_stiffness_matrix
from functions.ellipsoid_plot import generate_ellipsoid_plot

# Make a static folder to send images to openai
from fastapi.staticfiles import StaticFiles
# For unique file names
from uuid import uuid4
# Send asynchronous HTTP POST requests to the webhook URLs
import aiohttp
# For type hinting
from urllib.parse import urlparse
# For type hinting
from typing import List



# Initiate app
app = FastAPI()
# CORS origins that are allowed to connect to this server
origins = ["https://summary-sunbird-dashing.ngrok-free.app",
    "https://images-sunbird-dashing.ngrok-free.app",
    "https://frontend-example.ngrok-free.app",
    "https://ellipsoids-sunbird-dashing.ngrok-free.app",
    "https://stiffness-matrix-server.example.com" # Stiffness matrix server
]

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-matrix-url", "x-ellipsoid-url"]
)

# Store registered webhook URLs
webhook_urls: List[str] = []



@app.post("/register_webhook")
async def register_webhook(webhook_url: str):
    """
    Registers a webhook URL if it is valid and not already registered.

    Args:
        webhook_url (str): The URL to register as a webhook.

    Returns:
        dict: Confirmation message about the registration status.
    """
    # Validate the webhook URL
    parsed_url = urlparse(webhook_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise HTTPException(status_code=400, detail="Invalid webhook URL")
    
    # Add the webhook URL if it's not already registered
    if webhook_url not in webhook_urls:
        webhook_urls.append(webhook_url)
        print(webhook_urls)
        return {"message": f"Webhook registered successfully: {webhook_url}"}

    return {"message": f"Webhook already registered: {webhook_url}"}


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
    audio_file = "audio_inputs/voice.wav"
    transcript = speech_to_text(audio_file)
    print(transcript)
    if transcript is None:
        raise HTTPException(status_code=500, detail="Error decoding audio")
    response = get_gpt_response(transcript)
    print(response)
    if response is None:
        raise HTTPException(status_code=500, detail="Error fetching GPT response")
    update_conversation_history(transcript, response)
    text_to_speech_play_directly(response)

@app.post("/post_audio")
async def post_audio(
    file: UploadFile = File(...),
    image_url: str = Form(None)
):
    try:
        # Image URL handling
        print(f"Received image URL: {image_url}")

        # Audio processing code
        original_file_path = f"audio_inputs/{file.filename}"
        converted_file_path = f"audio_inputs/converted_{file.filename}"
        with open(original_file_path, "wb") as buffer:
            buffer.write(await file.read())

        ffmpeg.input(original_file_path).output(
            converted_file_path, ac=1, ar=16000
        ).global_args('-loglevel', 'error', '-hide_banner').run()

        transcript = speech_to_text(converted_file_path)
        if transcript is None:
            raise HTTPException(status_code=500, detail="Error decoding audio")
        # Response based on presence of image_url
        response = get_gpt_response_vlm(transcript, image_url) if image_url else get_gpt_response(transcript)
        if response is None:
            raise HTTPException(status_code=500, detail="Error fetching GPT response")
        print(response)
        # Attempt to extract stiffness matrix and handle None response safely
        result = extract_stiffness_matrix(response)
        stiffness_matrix, matrix_file_url, ellipsoid_plot_url = None, None, None

        if result:
            stiffness_matrix, matrix_file_url = result
            print("matrix_file_url: ", matrix_file_url)
            if stiffness_matrix:
                async with aiohttp.ClientSession() as session:
                    for webhook_url in webhook_urls:
                        try:
                            await session.post(webhook_url, json=stiffness_matrix)  # Send the matrix directly
                            print(f"Successfully notified webhook: {webhook_url}")
                        except Exception as e:
                            print(f"Failed to notify webhook {webhook_url}: {e}")
                ellipsoid_plot_url = generate_ellipsoid_plot(stiffness_matrix)
                print("ellipsoid_plot_url: ", ellipsoid_plot_url)
        else:
            print("No valid stiffness matrix found in the response.")

        # Update conversation history based on available image URL
        if image_url:
            update_conversation_history_vlm(transcript, image_url, response)
        else:
            update_conversation_history(transcript, response)

        # Generate audio response
        audio_file_path = text_to_speech(response)
        if not audio_file_path or not os.path.exists(audio_file_path):
            raise HTTPException(status_code=400, detail="Failed to generate audio")

        # Define the audio streaming function
        def iterfile():
            with open(audio_file_path, mode="rb") as file_like:
                yield from file_like

        # Include URLs in response headers only if they are available
        response_headers = {}
        if matrix_file_url:
            response_headers["x-matrix-url"] = matrix_file_url
        if ellipsoid_plot_url:
            response_headers["x-ellipsoid-url"] = ellipsoid_plot_url
        print("Response Headers:", response_headers)

        # Return the streaming response with the headers
        return StreamingResponse(iterfile(), media_type="audio/mpeg", headers=response_headers)

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up audio files
        if os.path.exists(original_file_path):
            os.remove(original_file_path)
        if os.path.exists(converted_file_path):
            os.remove(converted_file_path)


@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    try:
        if not os.path.exists("images"):
            os.makedirs("images")
        # Generate a unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid4()}.{file_extension}"
        file_path = f"images/{unique_filename}"
        # Save the file to the static/images folder
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        # Generate the file URL using your ngrok domain
        file_url = f"https://images-sunbird-dashing.ngrok-free.app/images/{unique_filename}"
        print(file_url)
        return file_url

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

