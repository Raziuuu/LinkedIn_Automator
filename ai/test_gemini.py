# ai/test_gemini.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load your Gemini API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
    response = model.generate_content("Suggest 3 creative names for a LinkedIn automation bot.")
    print("✅ Gemini API Response:")
    print(response.text)
except Exception as e:
    print(f"❌ Failed to connect to Gemini API:\n{e}")
