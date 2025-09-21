import whisper
import os

# Load Whisper model once
model = whisper.load_model("base")

def transcribe_audio(audio_path):
    """
    Transcribe user audio to text
    """
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        return ""
    result = model.transcribe(audio_path)
    return result["text"]
