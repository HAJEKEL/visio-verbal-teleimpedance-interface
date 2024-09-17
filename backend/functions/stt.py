from decouple import config
import wave
import json
import os
from vosk import Model, KaldiRecognizer

# Import custom functions
from .database import get_recent_conversation_history

model_path = os.path.join(os.path.dirname(__file__),"..","vosk-model-small-en-us-0.15")
model = Model(model_path)


# Convert audio to text using Vosk
def speech_to_text(audio_file):
    try:
        wf = wave.open(audio_file, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            raise ValueError("Audio file must be WAV format mono PCM.")

        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        transcript = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = rec.Result()
                transcript_data = json.loads(result)
                transcript += transcript_data.get("text", "")
        
        # Get any remaining partial result
        partial_result = rec.FinalResult()
        transcript_data = json.loads(partial_result)
        transcript += transcript_data.get("text", "")
        
        return transcript

    except Exception as e:
        print(e)
        return None

