from openai import OpenAI
from decouple import config
from pathlib import Path

# retrieve the API key from the .env file
organization = config("OPEN_AI_ORG")
api_key = config("OPEN_AI_KEY")
client = OpenAI(api_key=api_key, organization=organization)

# OpenAI gpt-4 function
# Generate text based on the prompt
def get_gpt_response(transcript):
    history = get_recent_conversation_history()
    user_message = {"role": "user", "content": transcript}
    history.append(user_message)
    try:
        response = openai_old.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=history
        )
        response_text = response["choices"][0]["message"]["content"]
        return response_text
    except Exception as e:
        print(e)
        return None


def text_to_speech(response):
  # initiate openai client
  speech_file_path = Path(__file__).parent / "speech.mp3"
  response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=response
  )

  response.stream_to_file(speech_file_path)