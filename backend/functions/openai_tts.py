from functions.openai_version import import_openai_version
from decouple import config
from pathlib import Path


# Load the latest version of the OpenAI package
openai_latest = import_openai_version('/app/openai_latest')
# retrieve the API key from the .env file
organization = config("OPEN_AI_ORG")
api_key = config("OPEN_AI_KEY")
print("openai latest", openai_latest)
#client = openai_latest.OpenAI(api_key=api_key, organization=organization)
def text_to_speech(response):
  # initiate openai client
  speech_file_path = Path(__file__).parent / "speech.mp3"
  response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=response
  )

  response.stream_to_file(speech_file_path)