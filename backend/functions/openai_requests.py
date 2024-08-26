import openai
from decouple import config

# retrieve the API key from the .env file
openai.organization = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")

# Import custom functions
from .database import get_recent_conversation_history

# open ai whipser function
# Convert audio to text
def convert_audio_to_text(audio_file):
    try:
        response = openai.Audio.transcribe("whisper-1", audio_file)
        transcript = response["text"]
        return transcript
    except Exception as e:
        print(e)
        return None

# OpenAI gpt-4 function
# Generate text based on the prompt
def get_gpt_response(transcript):
    history = get_recent_conversation_history()
    user_message = {"role": "user", "content": transcript}
    history.append(user_message)
    print(history)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=history
        )
        print(response)
        response_text = response.choices[0].message["content"]
        return response_text
    except Exception as e:
        print(e)
        return None