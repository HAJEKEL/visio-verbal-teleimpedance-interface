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

# OpenAI GPT-4 streaming function
def get_gpt_response(transcript):
    history = get_recent_conversation_history()
    user_message = {"role": "user", "content": transcript}
    history.append(user_message)
    
    try:
        # Create a stream using the OpenAI API
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[user_message],
            stream=True,
        )
        response_text = ""  # Initialize an empty string to accumulate the response

        
        # Loop over the chunks from the stream
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                response_text += content  # Accumulate the streamed content
        return response_text

    except Exception as e:
        print(e)
        return None

def text_to_speech(response_text):
    try:
        # Initiate OpenAI client to generate TTS audio
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=response_text,
        )

        # Save the generated speech to an MP3 file
        response.stream_to_file("output.mp3")
        print("Audio saved as output.mp3")

        # Play the MP3 file immediately using ffmpeg
        play_command = ["ffmpeg", "-i", "output.mp3", "-f", "pulse", "default"]
        subprocess.run(play_command)
        print("Playing audio...")

    except Exception as e:
        print(f"Error generating or playing speech: {e}")

