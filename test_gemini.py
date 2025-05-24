#!/usr/bin/env python
"""
Test script to verify Gemini API connectivity
"""
import os
from dotenv import load_dotenv

def test_gemini_api():
    print("Testing Gemini API connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if Gemini API key is set
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please add your API key to the .env file:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    
    # Try to import the Google Generative AI library
    try:
        import google.generativeai as genai
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
    except ImportError:
        print("❌ Google Generative AI package not found")
        print("Please install it with: pip install google-generativeai>=0.3.2")
        return False
    
    # Configure the Gemini API
    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured successfully")
    except Exception as e:
        print(f"❌ Failed to configure Gemini API: {e}")
        return False
    
    # Try a simple generation
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            "Generate one hashtag for LinkedIn about professional networking.",
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        print(f"✅ Test generation successful: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"❌ Test generation failed: {e}")
        return False

if __name__ == "__main__":
    if test_gemini_api():
        print("🎉 Gemini API is working properly!")
    else:
        print("❌ Gemini API test failed. Please fix the issues above.") 