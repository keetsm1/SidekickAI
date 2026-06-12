from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv("GEMINI_KEY")

client = genai.Client(api_key=gemini_key)