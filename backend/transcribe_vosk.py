import vosk

# Load the Vosk model
model = vosk.Model("vosk-model-small-en-us-0.15")

# Initialize the recognizer with the model
recognizer = vosk.KaldiRecognizer(model, 16000)

# Sample audio file for recognition
audio_file = "output.wav"

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
print(result)