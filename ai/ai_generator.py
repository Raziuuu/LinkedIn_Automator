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
    prompt = f"Generate 5 relevant LinkedIn hashtags for the topic: {topic}. Return only the hashtags separated by spaces, no explanations."
    hashtags_text = generate_text(prompt)
    return [tag.strip() for tag in hashtags_text.split() if tag.strip()]

def generate_alumni_message(name, college, department=None, graduation_year=None, purpose="connect"):
    """
    Generate a personalized message for reaching out to alumni.
    
    Args:
        name: Name of the alumni
        college: Name of the college/university
        department: Optional department or field of study
        graduation_year: Optional graduation year
        purpose: Purpose of the message (connect, mentorship, referral)
        
    Returns:
        A personalized message string
    """
    context = f"Generate a personalized LinkedIn message to reach out to {name}, an alumni of {college}"
    if department:
        context += f" who studied {department}"
    if graduation_year:
        context += f" and graduated in {graduation_year}"
    
    context += f". The purpose is to {purpose}. The message should be professional, friendly, and mention the shared connection of attending the same institution. Keep it concise (2-3 sentences) and ask for a brief conversation about their career journey. Do not include any placeholders like [Name] or [College] - use the actual values provided."
    
    return generate_text(context)

from utils.prompt_templates import get_alumni_message_template

# -------------------------------------------------------------------
# ✅ Expose Alumni Message Template via AI Interface
# -------------------------------------------------------------------
def generate_alumni_message_template(**kwargs):
    return get_alumni_message_template(**kwargs)

