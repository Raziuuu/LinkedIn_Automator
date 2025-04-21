import os
import requests
import base64
import io
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

# AI Backend Selection: 'mistral' (local) or 'gemini' (cloud)
AI_BACKEND = os.getenv("AI_BACKEND", "mistral").lower()

# Gemini API Setup
# Gemini Setup (Import globally once)
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# -------------------------------------------------------------------
# ✅ General Text Generation
# -------------------------------------------------------------------
def generate_text(prompt):
    if AI_BACKEND == "gemini":
        return generate_with_gemini(prompt)
    return generate_with_mistral(prompt)

def generate_with_mistral(prompt):
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"[❌] Mistral Error: {e}")
        return "(Error generating with Mistral)"

def generate_with_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[❌] Gemini Error: {e}")
        return "(Error generating with Gemini)"

# -------------------------------------------------------------------
# ✅ Follow-up Message Generator
# -------------------------------------------------------------------
def generate_connection_message(prompt):
    return generate_text(prompt)

# -------------------------------------------------------------------
# ✅ Basic Hashtag Generator (Based on caption)
# -------------------------------------------------------------------
def suggest_hashtags_basic(caption_text):
    prompt = f"Suggest 5 relevant LinkedIn hashtags for this caption: {caption_text}\nReturn them as a space-separated string."
    output = generate_text(prompt)
    return output.split() if output else []

# -------------------------------------------------------------------
# ✅ Image Captioning (Gemini Only)
# -------------------------------------------------------------------
def caption_image_with_gemini(image_path):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        image = Image.open(image_path)

        response = model.generate_content([
            "Describe this image for a LinkedIn post:",
            image
        ])
        return response.text.strip()
    except Exception as e:
        print(f"[❌] Gemini Vision Error: {e}")
        return "(Error generating image caption)"

def generate_caption_from_image(image_path):
    if AI_BACKEND == "gemini":
        return caption_image_with_gemini(image_path)
    else:
        raise NotImplementedError("Image captioning is currently only available via Gemini API.")

# -------------------------------------------------------------------
# ✅ Smart Topic & Hashtag Detection (Text + Optional Image)
# -------------------------------------------------------------------
def detect_topic_and_hashtags(caption_text, image_path=None):
    if image_path and AI_BACKEND == "gemini":
        image_caption = caption_image_with_gemini(image_path)
        caption_text += "\n" + image_caption

    prompt = (
        "You are an assistant that helps generate topics and hashtags for LinkedIn posts.\n"
        "Analyze the following post content and reply using exactly this format:\n\n"
        "Topic: <One concise phrase>\n"
        "Hashtags: #tag1 #tag2 #tag3 #tag4 #tag5\n\n"
        "No explanations, no options, no introductions. Just output exactly like the format above.\n\n"
        f"Post:\n{caption_text}"
    )

    output = generate_text(prompt)
    topic, hashtags = "General", []
    if "Topic:" in output:
        try:
            lines = output.splitlines()
            for line in lines:
                if line.startswith("Topic:"):
                    topic = line.split("Topic:")[-1].strip()
                elif line.startswith("Hashtags:"):
                    hashtags = line.split("Hashtags:")[-1].strip().split()
        except Exception as e:
            print(f"[⚠️] Parsing failed: {e}")
    return topic, hashtags

# -------------------------------------------------------------------
# ✅ Topic-Only Detection (For Simpler Logic)
# -------------------------------------------------------------------
def detect_topic(content, image_path=None):
    if image_path and AI_BACKEND == "gemini":
        image_caption = caption_image_with_gemini(image_path)
        content += "\n" + image_caption
    prompt = f"What is the main topic of this LinkedIn post:\n\n{content}\n\nRespond with a short phrase."
    return generate_text(prompt)

# -------------------------------------------------------------------
# ✅ Hashtag Suggestions Based on Topic
# -------------------------------------------------------------------
def suggest_hashtags(topic):
    prompt = f"Suggest 5 relevant LinkedIn hashtags for the topic: {topic}\nReturn them as a space-separated string."
    result = generate_text(prompt)
    return result.split()
