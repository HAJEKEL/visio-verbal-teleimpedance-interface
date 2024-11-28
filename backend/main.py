import os
import aiohttp
import logging
from uuid import uuid4
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Import necessary modules
from functions.speech_processor import SpeechProcessor
from functions.conversation_history_processor import ConversationHistoryProcessor
from functions.stiffness_matrix_processor import StiffnessMatrixProcessor
from functions.image_processor import ImageProcessor
from functions.webhook_processor import WebhookProcessor
from functions.eye_tracker_processor import EyeTrackerProcessor


class TeleimpedanceBackend:
    def __init__(self, environment: str, base_url: str, config_path: Optional[str] = None):
        """
        Initializes the backend with the specified environment and base URL.

        :param environment: The environment to use ("local", "public", etc.).
        :param base_url: The base URL for image and matrix services.
        :param config_path: Path to an optional JSON configuration file.
        """
        self.environment = environment
        self.base_url = base_url

        # Initialize FastAPI app
        self.app = FastAPI()

        # Set up CORS
        self.origins = [
            "http://localhost:5173", # Frontend
            "http://127.0.0.1:5173"
        ]
        self.setup_cors()

        # Initialize processors
        self.speech_processor = SpeechProcessor()
        self.conversation_history_processor = ConversationHistoryProcessor()
        self.stiffness_matrix_processor = StiffnessMatrixProcessor(use_public_urls=False)
        self.image_processor = ImageProcessor()
        self.webhook_processor = WebhookProcessor()
        self.eye_tracker_processor = EyeTrackerProcessor(eye_tracker_url="http://localhost:8011")
        self.webhook_urls = []  # Placeholder for webhook URLs

        # Set up routes
        self.setup_routes()

    def setup_cors(self):
        """
        Sets up CORS middleware.
        """
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["x-matrix-url", "x-ellipsoid-url"],
        )

    def setup_routes(self):
        """
        Sets up the routes for the application.
        """
        self.app.get("/")(self.root)
        self.app.get("/reset")(self.reset)
        self.app.post("/register_webhook")(self.register_webhook)
        self.app.post("/unregister_webhook")(self.unregister_webhook)
        self.app.get("/list_webhooks")(self.list_webhooks)
        self.app.post("/upload_image")(self.upload_image)
        self.app.post("/post_audio")(self.post_audio)

    async def root(self):
        """
        Root endpoint.
        """
        return {"message": "This is the root of the visio-verbal teleimpedance backend"}

    async def reset(self):
        """
        Resets the conversation history.
        """
        return self.conversation_history_processor.reset_conversation_history()

    async def register_webhook(self, webhook_url: str):
        """
        Registers a webhook URL.
        """
        try:
            message = self.webhook_processor.register_webhook(webhook_url)
            return {"message": message}
        except Exception as e:
            logging.error(f"Error registering webhook: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def unregister_webhook(self, webhook_url: str):
        """
        Unregisters a webhook URL.
        """
        try:
            message = self.webhook_processor.unregister_webhook(webhook_url)
            return {"message": message}
        except Exception as e:
            logging.error(f"Error unregistering webhook: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def list_webhooks(self):
        """
        Lists all currently registered webhook URLs.
        """
        webhooks = self.webhook_processor.list_webhooks()
        return {"registered_webhooks": webhooks}

    async def upload_image(self, file: UploadFile):
        """
        Uploads an image and processes it.
        """
        file_url = await self.image_processor.process_uploaded_image(file, self.base_url)
        if file_url:
            return {"file_url": file_url}
        else:
            raise HTTPException(status_code=500, detail="Image processing failed")

    async def calibrate(self):
        """
        Endpoint to calibrate the eye tracker.
        """
        return await self.eye_tracker_processor.calibrate()

    async def capture_snapshot(self):
        """
        Endpoint to capture a snapshot from the eye tracker.
        """
        return await self.eye_tracker_processor.capture_snapshot()

    
    async def post_audio(self, file: UploadFile, image_url: Optional[str] = Form(None)):
        """
        Processes uploaded audio and generates a response.
        """
        converted_audio_file_path = None
        try:
            # Convert audio format
            converted_audio_file_path = await self.speech_processor.convert_audio_format(file)

            # Transcribe audio
            transcript = self.speech_processor.speech_to_text(converted_audio_file_path)
            if transcript is None:
                raise HTTPException(status_code=500, detail="Error decoding audio")

            # Fetch GPT response
            if image_url:
                response = self.speech_processor.get_gpt_response_vlm(transcript, image_url)
            else:
                response = self.speech_processor.get_gpt_response_vlm(transcript)

            # Process stiffness matrix
            result = self.stiffness_matrix_processor.extract_stiffness_matrix(response)
            stiffness_matrix, matrix_file_url, ellipsoid_plot_url = None, None, None

            if result:
                stiffness_matrix, matrix_file_url = result
                async with aiohttp.ClientSession() as session:
                    for webhook_url in self.webhook_urls:
                        try:
                            await session.post(webhook_url, json=stiffness_matrix)
                        except Exception as e:
                            logging.error(f"Failed to notify webhook {webhook_url}: {str(e)}")
                ellipsoid_plot_url = self.stiffness_matrix_processor.generate_ellipsoid_plot(stiffness_matrix)

            # Update conversation history
            if image_url:
                self.conversation_history_processor.update_conversation_history(transcript, image_url, response)
            else:
                self.conversation_history_processor.update_conversation_history(transcript, response)

            # Generate TTS audio
            audio_file_path = self.speech_processor.text_to_speech(response)
            if not audio_file_path or not os.path.exists(audio_file_path):
                raise HTTPException(status_code=500, detail="Failed to generate audio")

            def iterfile():
                with open(audio_file_path, mode="rb") as file_like:
                    yield from file_like

            headers = {}
            if matrix_file_url:
                headers["x-matrix-url"] = matrix_file_url
            if ellipsoid_plot_url:
                headers["x-ellipsoid-url"] = ellipsoid_plot_url

            return StreamingResponse(iterfile(), media_type="audio/mpeg", headers=headers)

        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        finally:
            if converted_audio_file_path and os.path.exists(converted_audio_file_path):
                os.remove(converted_audio_file_path)


# Instantiate and expose the app
backend = TeleimpedanceBackend(environment="local", base_url="https://images-sunbird-dashing.ngrok-free.app")
app = backend.app
