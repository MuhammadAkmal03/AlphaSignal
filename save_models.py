import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

with open("available_models.txt", "w", encoding="utf-8") as f:
    f.write("Available Gemini Models:\n")
    f.write("="*60 + "\n\n")
    
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            f.write(f"{model.name}\n")

print("Models saved to available_models.txt")
