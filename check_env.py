import os
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
print(f"Gemini API Key: {gemini_key[:20] if gemini_key else 'NOT FOUND'}...")
print(f"Key length: {len(gemini_key) if gemini_key else 0}")
print(f"Key is truthy: {bool(gemini_key)}")
