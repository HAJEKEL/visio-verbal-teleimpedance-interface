from app.utils import import_openai_version
from decouple import config

# Load the latest version of the OpenAI package
openai_latest = import_openai_version('/app/openai_latest')
# retrieve the API key from the .env file
organization = config("OPEN_AI_ORG")
api_key = config("OPEN_AI_KEY")
# initiate openai client
client = OpenAI(organization,api_key)

speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="alloy",
  input="Today is a wonderful day to build something people love!"
)

response.stream_to_file(speech_file_path)