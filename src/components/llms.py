from openai import OpenAI
from src.prompt import transcription_prompt
import os
from dotenv import load_dotenv
load_dotenv()

TRANSCRIPTION_MODEL = os.getenv("TRANSCRIPTION_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
class Models: 
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)


    async def transcription_model(self,audio_file):
        transcription = self.client.audio.transcriptions.create(
            model = TRANSCRIPTION_MODEL,
            file = audio_file,
            response_format='text',
            prompt=transcription_prompt
        )
        return transcription.text
