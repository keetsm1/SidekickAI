from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

default_key = os.getenv("GEMINI_KEY")

def get_client(api_key=None):
    key = api_key if api_key else default_key
    return genai.Client(api_key=key)

client = get_client()
