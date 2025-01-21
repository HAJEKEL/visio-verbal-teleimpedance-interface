import os
import sys
import aiohttp
import logging
from typing import List
from dotenv import load_dotenv, find_dotenv
from uuid import uuid4
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from pathlib import Path

# Ensure `functions/` is discoverable
sys.path.append(str(Path(__file__).resolve().parent / "functions"))

# Import necessary modules
from functions.speech_processor import SpeechProcessor
from functions.conversation_history_processor import ConversationHistoryProcessor
from functions.stiffness_matrix_processor import StiffnessMatrixProcessor
from functions.image_processor import ImageProcessor
from functions.webhook_processor import WebhookProcessor
from functions.eye_tracker_processor import EyeTrackerProcessor

# Environment variables
from decouple import config, RepositoryEnv

# Retrieve the required environment variables using config()
try:
    # Load ports and other necessary variables
    BACKEND_MAIN_PORT = config("BACKEND_MAIN_PORT")  # Port for the main backend
    PUBLIC_STATIC_SERVER_PORT = config("PUBLIC_STATIC_SERVER_PORT")  # Port for public static server
    LOCAL_STATIC_SERVER_PORT = config("LOCAL_STATIC_SERVER_PORT")  # Port for local static server
    EYE_TRACKER_PORT = config("EYE_TRACKER_PORT")  # Port for eye tracker
    SIGMA_SERVER_PORT = config("SIGMA_SERVER_PORT")  # Port for Sigma7 server
    FRONTEND_PORT = config("FRONTEND_PORT")  # Port for the frontend
    # Other variables
    ENVIRONMENT = config("ENVIRONMENT", default="local")  # Default to local environment
    LOG_LEVEL = config("LOG_LEVEL", default="INFO")  # Logging level

except KeyError as e:
    logging.error(f"Environment variable {e.args[0]} is not set.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL.upper(),
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Assemble URLs using localhost and ports
BACKEND_URL = f"http://localhost:{BACKEND_MAIN_PORT}"  # Backend main URL
PUBLIC_STATIC_SERVER_URL = f"http://localhost:{PUBLIC_STATIC_SERVER_PORT}"  # Public static server
LOCAL_STATIC_SERVER_URL = f"http://localhost:{LOCAL_STATIC_SERVER_PORT}"  # Local static server
EYE_TRACKER_URL = config("EYE_TRACKER_URL")  # Eye tracker URL
SIGMA_SERVER_URL = f"http://sigma7:{SIGMA_SERVER_PORT}"  # Sigma7 server URL

# Optionally log the assembled URLs for debugging
logging.info(f"Backend URL: {BACKEND_URL}")
logging.info(f"Public Static Server URL: {PUBLIC_STATIC_SERVER_URL}")
logging.info(f"Local Static Server URL: {LOCAL_STATIC_SERVER_URL}")
logging.info(f"Eye Tracker URL: {EYE_TRACKER_URL}")
logging.info(f"Sigma7 Server URL: {SIGMA_SERVER_URL}")



class TeleimpedanceBackend:
    def __init__(self, environment: str, base_url: str, frontend_port: str, eye_tracker_url: str, sigma_server_url: str, log_level: str):
        """
        Initializes the backend with the specified environment and base URL.

        :param environment: The environment to use ("local", "public", etc.).
        :param base_url: The base URL for image and matrix services.
        :param config_path: Path to an optional JSON configuration file.
        """

        self.log_level = log_level.upper()
        self.environment = environment
        self.base_url = base_url
        self.origins = f"http://localhost:{frontend_port}"

        self.eye_tracker_url = eye_tracker_url
        self.sigma_server_url = sigma_server_url  # Added this line

        # Initialize FastAPI app
        self.app = FastAPI()

        # Set up CORS
        self.setup_cors()

        # Initialize processors
        self.speech_processor = SpeechProcessor()
        self.conversation_history_processor = ConversationHistoryProcessor()
        self.stiffness_matrix_processor = StiffnessMatrixProcessor(use_public_urls=False, local_static_server_port=LOCAL_STATIC_SERVER_PORT)
        self.image_processor = ImageProcessor()
        self.webhook_processor = WebhookProcessor()
        self.eye_tracker_processor = EyeTrackerProcessor(eye_tracker_url=eye_tracker_url)
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
        self.app.get("/", response_class=HTMLResponse)(self.root)
        self.app.get("/reset")(self.reset)
        self.app.post("/register_webhook")(self.register_webhook)
        self.app.post("/unregister_webhook")(self.unregister_webhook)
        self.app.get("/list_webhooks")(self.list_webhooks)
        self.app.post("/upload_image")(self.upload_image)
        self.app.post("/post_audio")(self.post_audio)
        self.app.get("/calibrate")(self.calibrate)
        self.app.get("/capture_snapshot")(self.capture_snapshot)
        self.app.get("/sigma/start")(self.start_sigma)
        self.app.get("/sigma/stop")(self.stop_sigma)
        self.app.get("/sigma/set_zero")(self.set_zero_sigma)
        self.app.get("/sigma/autoinit")(self.autoinit_sigma)
        self.app.get("/sigma/initialize")(self.initialize_sigma)

    async def root(self):
        """
        Root endpoint providing an HTML overview of the backend API.
        """
        # Define the path to the HTML file
        html_file_path = os.path.join(os.path.dirname(__file__), "templates", "main_root_page.html")
        
        # Read the HTML content
        try:
            with open(html_file_path, "r", encoding="utf-8") as file:
                html_content = file.read()
        except FileNotFoundError:
            return HTMLResponse(content="<h1>Error: root_page.html not found</h1>", status_code=500)
        except Exception as e:
            return HTMLResponse(content=f"<h1>Error: {e}</h1>", status_code=500)

        return HTMLResponse(content=html_content)

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
    
    async def start_sigma(self):
        """
        Sends a start command to the Sigma7 server.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.sigma_server_url}/control", data="start") as resp:
                    if resp.status == 200:
                        return {"message": "Sigma7 started successfully."}
                    else:
                        text = await resp.text()
                        raise HTTPException(status_code=resp.status, detail=text)
        except Exception as e:
            logging.error(f"Error starting Sigma7: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def stop_sigma(self):
        """
        Sends a stop command to the Sigma7 server.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.sigma_server_url}/control", data="stop") as resp:
                    if resp.status == 200:
                        return {"message": "Sigma7 stopped successfully."}
                    else:
                        text = await resp.text()
                        raise HTTPException(status_code=resp.status, detail=text)
        except Exception as e:
            logging.error(f"Error stopping Sigma7: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def set_zero_sigma(self):
        """
        Sends a set_zero command to the Sigma7 server.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.sigma_server_url}/control", data="set_zero") as resp:
                    if resp.status == 200:
                        return {"message": "Sigma7 zero position set successfully."}
                    else:
                        text = await resp.text()
                        raise HTTPException(status_code=resp.status, detail=text)
        except Exception as e:
            logging.error(f"Error setting zero position on Sigma7: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def autoinit_sigma(self):
        """
        Sends a request to autoinit the Sigma7 server.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.sigma_server_url}/autoinit") as resp:
                    if resp.status == 200:
                        return {"message": "Sigma7 autoinit completed successfully."}
                    else:
                        text = await resp.text()
                        raise HTTPException(status_code=resp.status, detail=text)
        except Exception as e:
            logging.error(f"Error running autoinit on Sigma7: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def initialize_sigma(self):
        """
        Sends an initialize command to the Sigma7 server.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.sigma_server_url}/control", data="initialize") as resp:
                    if resp.status == 200:
                        return {"message": "Sigma7 initialized successfully."}
                    else:
                        text = await resp.text()
                        raise HTTPException(status_code=resp.status, detail=text)
        except Exception as e:
            logging.error(f"Error initializing Sigma7: {type(e).__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    
    async def post_audio(self, file: UploadFile, image_url: Optional[str] = Form(None)):
        """
        Processes uploaded audio and generates a response.
        """
        converted_audio_file_path = None
        try:
            # Log received data for debugging
            logging.info(f"Received audio file: {file.filename}, Content-Type: {file.content_type}")
            logging.info(f"Received image URL: {image_url}")

            # Convert audio format
            converted_audio_file_path = await self.speech_processor.convert_audio_format(file)
            # Convert local image url to public image url
            if image_url:
                image_url = self.speech_processor.convert_local_image_url_to_public(image_url)
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
                logging.info(f"Stiffness matrix to send: {stiffness_matrix}")
                async with aiohttp.ClientSession() as session:
                    for webhook_url in self.webhook_urls:
                        try:
                            await session.post(webhook_url, json=stiffness_matrix)
                        except Exception as e:
                            logging.error(f"Failed to notify webhook {webhook_url}: {str(e)}")
                ellipsoid_plot_url = self.stiffness_matrix_processor.generate_ellipsoid_plot(stiffness_matrix)

            # Update conversation history
            if image_url:
                # second param is response, third is image_url
                self.conversation_history_processor.update_conversation_history(transcript, response, image_url)
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

backend = TeleimpedanceBackend(
    environment=ENVIRONMENT,
    base_url=PUBLIC_STATIC_SERVER_URL,
    frontend_port=FRONTEND_PORT,
    eye_tracker_url=EYE_TRACKER_URL,
    sigma_server_url=SIGMA_SERVER_URL,  # Added this line
    log_level=LOG_LEVEL
)
app = backend.app