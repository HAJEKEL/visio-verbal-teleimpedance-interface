from vosk import Model, KaldiRecognizer
import json
import os

# Load the Vosk model
model_path = os.path.join(os.path.dirname(__file__), "..", "vosk-model-small-en-us-0.15")

model = Model(model_path)

# Function to transcribe audio
def speech_to_text(audio_file):
    try:
        # Initialize the recognizer with the model
        recognizer = KaldiRecognizer(model, 16000)
        
        transcript = ""
        
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
        
        return transcript_data.get("text", "")
    except Exception as e:
        print(e)
        return None

# # Example usage
# audio_file = os.path.join(os.path.dirname(__file__), "..", "data", "voice.wav")
# transcript = speech_to_text(audio_file)
# print(transcript)
