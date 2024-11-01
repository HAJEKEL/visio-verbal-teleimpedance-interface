import openai
from decouple import config
from pathlib import Path
import os
import subprocess
import re

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
            model="gpt-4o",
            messages=history,
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
        # Define pattern to locate the stiffness matrix
        stiffness_pattern = r"### Stiffness Matrix(?: \(Recommended Values\))?(?:\n|.)*"
        
        # Filter out the stiffness matrix part from the response text
        filtered_text = re.sub(stiffness_pattern, "", response_text).strip()
        
        # Initiate OpenAI client to generate TTS audio with filtered text
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
        print(f"Error generating speech: {e}")
        return None