import openai
from decouple import config

# retrieve the API key from the .env file
openai.organization = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")

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

