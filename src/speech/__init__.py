import sys
sys.path.append('..')

import whisper

class SpeechRecognition:
    def __init__(self) -> None:
        self.model = whisper.load_model("small")
    
    def get_text(self, file_path):
        res = self.model.transcribe(file_path)

        return res["text"]