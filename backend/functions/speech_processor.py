import os
import sys
import json
import uuid
import time
import logging
import requests
import re
from pathlib import Path
import ffmpeg

# Speech Recognition Imports
from vosk import Model, KaldiRecognizer, SetLogLevel
# OpenAI API Imports
import openai
from decouple import config, RepositoryEnv

# Import the ConversationManager class
from conversation_history_processor import ConversationHistoryProcessor

class SpeechProcessor:
    """
    A class to handle speech-to-text (STT), response generation using OpenAI's API, and text-to-speech (TTS).
    """
    # Class variable for Vosk model path
    VOSK_MODEL_PATH = Path(__file__).resolve().parent.parent / "vosk-model-small-en-us-0.15"
    
    def __init__(self, log_level: int = -1):
        # Initialize Vosk model for STT
        SetLogLevel(log_level)  # Suppress Vosk logs
        self.model = self.load_vosk_model()

        # Initialize OpenAI client
        self.initialize_openai_client()

        # Initialize the ConversationManager
        self.conversation_history_processor = ConversationHistoryProcessor()

    def add_parent_to_sys_path():
        """
        Adds the parent directory to sys.path for module imports.
        """
        parent_dir = Path(__file__).resolve().parent
        if str(parent_dir) not in sys.path:
            sys.path.append(str(parent_dir))
            logging.info(f"Added {parent_dir} to sys.path")

    async def convert_audio_format(self, audio_file):
        """
        Converts the uploaded audio file to the required format using ffmpeg.

        Parameters:
            audio_file: An UploadFile object or similar file-like object supporting asynchronous reading.

        Returns:
            str: Path to the converted audio file, or None if conversion failed.
        """
        try:
            # Ensure the audio_inputs directory exists
            os.makedirs("audio_inputs", exist_ok=True)

            original_file_path = f"audio_inputs/{audio_file.filename}"
            converted_file_path = f"audio_inputs/converted_{audio_file.filename}"

            # Read and save the original audio file asynchronously
            with open(original_file_path, "wb") as buffer:
                data = await audio_file.read()
                buffer.write(data)
            logging.info(f"Original audio file saved to {original_file_path}")

            # Convert the audio file using ffmpeg
            (
                ffmpeg
                .input(original_file_path)
                .output(converted_file_path, ac=1, ar=16000)
                .global_args('-loglevel', 'error', '-hide_banner')
                .run()
            )
            logging.info(f"Audio file converted and saved to {converted_file_path}")

            return converted_file_path

        except ffmpeg.Error as e:
            logging.error(f"FFmpeg error during audio conversion: {e.stderr.decode()}")
            return None
        except Exception as e:
            logging.error(f"Error converting audio file: {e}")
            return None
    
    def load_vosk_model(self):
        """
        Loads the Vosk speech recognition model.
        """
        model_path = os.path.join(os.path.dirname(__file__), "..", "vosk-model-small-en-us-0.15")
        if not os.path.exists(model_path):
            logging.error(f"Vosk model not found at {model_path}, either download it or update the path using the class method .")
            raise FileNotFoundError(f"Vosk model not found at {model_path}")
        model = Model(model_path)
        logging.info("Vosk model loaded successfully.")
        return model

    def initialize_openai_client(self):
        """
        Initializes the OpenAI API client.
        """
        organization = config("OPEN_AI_ORG")
        api_key = config("OPEN_AI_KEY")
        self.client = openai.OpenAI(api_key=api_key, organization=organization)
        logging.info("OpenAI client initialized successfully.")

    def speech_to_text(self, audio_file):
        """
        Converts speech in an audio file to text using Vosk.

        Parameters:
            audio_file (str): Path to the audio file.

        Returns:
            str: The transcribed text.
        """
        try:
            # Initialize the recognizer with the model
            recognizer = KaldiRecognizer(self.model, 16000)

            # Open the audio file
            with open(audio_file, "rb") as audio:
                while True:
                    # Read a chunk of the audio file
                    data = audio.read(4000)
                    if len(data) == 0:
                        break
                    # Recognize the speech in the chunk
                    recognizer.AcceptWaveform(data)

            # Get the final recognized result
            result = recognizer.FinalResult()
            transcript_data = json.loads(result)

            transcript = transcript_data.get("text", "")
            logging.info(f"Transcription completed: {transcript}")
            return transcript

        except Exception as e:
            logging.error(f"Error in speech_to_text: {e}")
            return None

    def get_gpt_response_vlm(self, transcript, image_url=None):
        """
        Generates a response using OpenAI's GPT model, optionally including an image.

        Parameters:
            transcript (str): The user's input text.
            image_url (str, optional): URL of the image to include in the prompt.

        Returns:
            str: The generated response from GPT.
        """
        try:
            # Get recent conversation history
            history = self.conversation_history_processor.get_recent_conversation_history()

            # Prepare user message
            content = [{"type": "text", "text": transcript}]
            if image_url:
                # Add a cache-busting parameter to ensure fresh requests
                image_url_with_cache = f"{image_url}?cache_bust={int(time.time())}"

                # Verify URL accessibility before proceeding
                response = requests.get(image_url_with_cache, timeout=20)
                if response.status_code != 200:
                    logging.error(f"Image URL {image_url_with_cache} is inaccessible with status code {response.status_code}")
                    return None

                content.append({"type": "image_url", "image_url": {"url": image_url_with_cache}})

            user_message = {
                "role": "user",
                "content": content
            }

            # Append the user message to the history
            history.append(user_message)
            logging.info("User message added to conversation history.")
            client = self.client
            # Call the OpenAI API
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=history,
                stream=True,
            )
            gpt_response = ""  # Initialize an empty string to accumulate the response

            
            # Loop over the chunks from the stream
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    gpt_response += content  # Accumulate the streamed content
            logging.info(f"GPT response received: {gpt_response}")

            # Update the conversation history with the assistant's response
            self.conversation_history_processor.update_conversation_history(transcript, gpt_response, image_url=image_url)

            return gpt_response

        except Exception as e:
            logging.error(f"Error in get_gpt_response_vlm: {e}")
            return None

    def text_to_speech(self, text):
        """
        Converts text to speech and saves it as an audio file.

        Parameters:
            text (str): The text to convert to speech.

        Returns:
            str: Path to the generated audio file, or False if an error occurred.
        """
        try:
            # Define pattern to locate the stiffness matrix
            stiffness_pattern = r"### Stiffness Matrix(?: \(Recommended Values\))?(?:\n|.)*"
            
            # Filter out the stiffness matrix part from the response text
            filtered_text = re.sub(stiffness_pattern, "", text).strip()

            # If nothing remains after filtering, set a default message
            if not filtered_text:
                filtered_text = (
                    "The stiffness matrix has been adjusted. These are the stiffness matrix and stiffness ellipsoid."
                )

            # Initiate OpenAI client to generate TTS audio with filtered text
            client = self.client
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=filtered_text,
            )
            
            # Save the generated speech to an MP3 file
            path = os.path.join(os.path.dirname(__file__), '..', 'audio_outputs', 'output.mp3')
            response.stream_to_file(path)
            return path

        except Exception as e:
            logging.error(f"Error in text_to_speech: {e}")
            return False


if __name__ == "__main__":
    # Create an instance of SpeechProcessor
    processor = SpeechProcessor()

    # Test speech_to_text
    audio_file_path = os.path.join(os.path.dirname(__file__), "..", "audio_inputs/voice.wav")
    transcript = processor.speech_to_text(audio_file_path)
    # Test get_gpt_response_vlm
    image_url = "https://www.xenos.nl/pub/cdn/582043/800/582043.jpg"
    gpt_response = processor.get_gpt_response_vlm(transcript, image_url=image_url)
    # Test text_to_speech
    processor.text_to_speech(gpt_response)
