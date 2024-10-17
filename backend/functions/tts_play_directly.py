import openai
from decouple import config
from pathlib import Path
import os
import subprocess

# Custom function imports
from functions.database import get_recent_conversation_history

# Retrieve the API key from the .env file
organization = config("OPEN_AI_ORG")
api_key = config("OPEN_AI_KEY")
client = openai.OpenAI(api_key=api_key, organization=organization)

def text_to_speech_play_directly(response_text):
    try:
        # Initiate OpenAI client to generate TTS audio
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=response_text,
        )

        # Save the generated speech to an MP3 file
        response.stream_to_file("audio_outputs/output.mp3")
        print("Audio saved as output.mp3")

        # Play the MP3 file using ffplay (more reliable for audio playback)
        play_command = ["ffplay", "-autoexit", "-nodisp", "output.mp3"]
        subprocess.run(play_command)
        print("Playing audio...")

    except Exception as e:
        print(f"Error generating or playing speech: {e}")
