import sys
sys.path.append('..')

# import whisper
import openai
import os

openai.api_key=os.environ["OPENAI_API_KEY"]

class SpeechRecognition:
    def __init__(self) -> None:
        self.model=None #whisper.load_model("small")
    
    def get_text(self, file_path):
        file_path=open(file_path, "rb")
        responce=openai.Audio.transcribe("whisper-1", file_path) 
        #self.model.transcribe(file_path)
        return str()