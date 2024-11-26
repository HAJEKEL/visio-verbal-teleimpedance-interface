import os
import aiohttp
import logging
from uuid import uuid4
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from urllib.parse import urlparse

# Import classes from modules
from functions.speech_processor import SpeechProcessor
from functions.conversation_history_processor import ConversationHistoryProcessor
from functions.stiffness_matrix_processor import StiffnessMatrixProcessor
from functions.image_processor import ImageProcessor
from functions.webhook_processor import WebhookProcessor

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
# Disable all Vosk logs
os.environ["VOSK_LOG_LEVEL"] = "-1"  

# Initiate app
app = FastAPI()
# CORS origins that are allowed to connect to this server
# CORS configuration
origins = [
    "https://summary-sunbird-dashing.ngrok-free.app",
    "https://images-sunbird-dashing.ngrok-free.app",
    "https://frontend-example.ngrok-free.app",
    "https://ellipsoids-sunbird-dashing.ngrok-free.app",
    "https://stiffness-matrix-server.example.com",  # Stiffness matrix server
    "http://localhost:5173",        # Frontend
    "http://127.0.0.1:5173",        # Frontend (127.0.0.1)
    "http://localhost:5174",        # Frontend
    "http://127.0.0.1:5174",        # Frontend (127.0.0.1)
    "http://localhost:8002",        # Ellipsoid server
    "http://127.0.0.1:8002",        # Ellipsoid server (127.0.0.1)
    "http://localhost:8003",        # Stiffness matrix server
    "http://127.0.0.1:8003",        # Stiffness matrix server (127.0.0.1)
    "http://localhost:8080",        # Sigma.7 server
    "http://127.0.0.1:8080"         # Sigma.7 server (127.0.0.1)
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


# Create instances of the classes
speech_processor = SpeechProcessor()
conversation_history_processor = ConversationHistoryProcessor()
stiffness_matrix_processor = StiffnessMatrixProcessor(use_public_urls=False)
image_processor = ImageProcessor()
webhook_processor = WebhookProcessor()


base_url = "https://images-sunbird-dashing.ngrok-free.app"  # Update with your actual base URL

@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "This is the root of the visio-verbal teleimpedance backend"}

@app.get("/reset")
async def reset():
    """
    Resets the conversation history.
    """
    return conversation_manager.reset_conversation_history()

@app.post("/register_webhook")
async def register_webhook(webhook_url: str):
    """
    Registers a webhook URL if it is valid and not already registered.
    """
    try:
        message = webhook_manager.register_webhook(webhook_url)
        return {"message": message}
    except HTTPException as e:
        logging.error(f"Error registering webhook: {e.detail}")
        raise e

@app.post("/unregister_webhook")
async def unregister_webhook(webhook_url: str):
    """
    Unregisters a webhook URL if it is currently registered.
    """
    try:
        message = webhook_manager.unregister_webhook(webhook_url)
        return {"message": message}
    except HTTPException as e:
        logging.error(f"Error unregistering webhook: {e.detail}")
        raise e

@app.get("/list_webhooks")
async def list_webhooks():
    """
    Lists all currently registered webhook URLs.
    """
    webhooks = webhook_manager.list_webhooks()
    return {"registered_webhooks": webhooks}

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    file_url = await image_processor.process_uploaded_image(file, base_url)
    if file_url:
        return {"file_url": file_url}
    else:
        raise HTTPException(status_code=500, detail="Image processing failed")



@app.post("/post_audio")
async def post_audio(
    file: UploadFile = File(...),
    image_url: str = Form(None)
):
    try:
        converted_audio_file_path = speech_processor.convert_file_path(original_file_path)
        transcript = speech_processor.speech_to_text(converted_file_path)
        if transcript is None:
            raise HTTPException(status_code=500, detail="Error decoding audio")
        # Response based on presence of image_url
        response = speech_processor.get_gpt_response_vlm(transcript, image_url) if image_url else speech_processor.get_gpt_response_vlm(transcript)
        if response is None:
            raise HTTPException(status_code=500, detail="Error fetching GPT response")
        # Attempt to extract stiffness matrix and handle None response safely
        result = stiffness_matrix_processor.extract_stiffness_matrix(response)
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
                ellipsoid_plot_url = stiffness_matrix_processor.generate_ellipsoid_plot(stiffness_matrix)
                print("ellipsoid_plot_url: ", ellipsoid_plot_url)
        else:
            print("No valid stiffness matrix found in the response.")

        # Update conversation history based on available image URL
        if image_url:
            conversation_history_processor.update_conversation_history(transcript, image_url, response)
        else:
            conversation_history_processor.update_conversation_history(transcript, response)

        # Generate audio response
        audio_file_path = speech_processor.text_to_speech(response)
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




