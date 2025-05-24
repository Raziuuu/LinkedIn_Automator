import os
import io
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

# Gemini API Setup
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    
    # Configure Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
except ImportError:
    raise ImportError("Google Generative AI package not found. Please install with: pip install google-generativeai")

# Model name constant
GEMINI_MODEL = "gemini-1.5-flash"

# -------------------------------------------------------------------
# ✅ General Text Generation
# -------------------------------------------------------------------
def generate_text(prompt):
    return generate_with_gemini(prompt)

def generate_with_gemini(prompt):
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        return response.text.strip()
    except Exception as e:
        print(f"[❌] Gemini Error: {e}")
        return "(Error generating with Gemini)"

# -------------------------------------------------------------------
# ✅ LinkedIn Message Enhancement
# -------------------------------------------------------------------
def enhance_linkedin_message(base_message, topic, tone="professional"):
    """
    Enhance a LinkedIn message with Gemini based on a topic and tone.
    
    Args:
        base_message (str): The base template message
        topic (str): The topic or context for the message
        tone (str): The desired tone (professional, friendly, casual)
    
    Returns:
        str: Enhanced message
    """
    prompt = f"""
    Enhance this LinkedIn message keeping the same {tone} tone, but incorporating the topic: '{topic}'.
    
    Original template: {base_message}
    
    Rules:
    1. Keep the message under 400 characters
    2. Maintain the {tone} tone
    3. Address the recipient as {{name}} (keep these placeholders)
    4. Make it specific to the topic: {topic}
    5. Make it sound natural and conversational
    6. Include a clear call to action
    
    Return only the enhanced message text, preserving the {{name}} placeholder.
    """
    
    enhanced_message = generate_text(prompt)
    
    # Clean up the enhanced message
    if enhanced_message:
        enhanced_message = enhanced_message.strip('"\'')
        return enhanced_message
    
    # Return original if enhancement fails
    return base_message

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
# ✅ Image Captioning (Gemini)
# -------------------------------------------------------------------
def caption_image_with_gemini(image_path):
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
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
    return caption_image_with_gemini(image_path)

# -------------------------------------------------------------------
# ✅ Smart Topic & Hashtag Detection (Text + Optional Image)
# -------------------------------------------------------------------
def detect_topic_and_hashtags(caption_text, image_path=None):
    if image_path:
        image_caption = caption_image_with_gemini(image_path)
        caption_text += "\n" + image_caption

    prompt = (
        "You are an assistant that helps generate topics and hashtags for LinkedIn posts.\n"
        "Analyze the following post content and reply using exactly this format:\n\n"
        "Topic: <One concise phrase that captures the professional focus>\n"
        "Hashtags: #tag1 #tag2 #tag3 #tag4 #tag5\n\n"
        "Hashtag guidelines:\n"
        "1. Be specific and relevant to the professional context\n"
        "2. Avoid generic hashtags like #motivation, #success, or #life\n"
        "3. Include at least one industry-specific hashtag\n"
        "4. Include at least one skill-related hashtag if applicable\n"
        "5. Maximum 5 hashtags total\n\n"
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
    if image_path:
        image_caption = caption_image_with_gemini(image_path)
        content += "\n" + image_caption
    prompt = f"What is the main topic of this LinkedIn post:\n\n{content}\n\nRespond with a short phrase."
    return generate_text(prompt)

# -------------------------------------------------------------------
# ✅ Hashtag Suggestions Based on Topic
# -------------------------------------------------------------------
def suggest_hashtags(topic):
    prompt = (
        f"Suggest 3-5 relevant LinkedIn hashtags for the topic: {topic}\n"
        "Guidelines:\n"
        "1. Be specific and relevant to the professional context\n"
        "2. Avoid generic hashtags like #motivation, #success, or #life\n"
        "3. Include at least one industry-specific hashtag\n"
        "4. Include at least one skill-related hashtag if applicable\n"
        "5. Make hashtags concise - preferably 1-2 words each\n"
        "Return them as a space-separated string without explanations."
    )
    result = generate_text(prompt)
    return result.split()

# -------------------------------------------------------------------
# ✅ Caption Enhancement
# -------------------------------------------------------------------
def enhance_caption(caption):
    prompt = (
        "You are a professional LinkedIn content writer. Enhance and restructure this post caption following the exact structure below:\n\n"
        "# Lines 1-2: HOOK – Grab attention\n"
        "# Use a bold statement, thought-provoking question, or relatable problem.\n\n"
        "# Lines 3-6: CONTEXT – Explain what you're working on or the value being shared\n"
        "# Keep sentences short, use line breaks, and focus on benefits not just features.\n\n"
        "# Lines 7-8: CHALLENGE or PERSONAL TOUCH – What was a roadblock or learning?\n"
        "# Add authenticity and encourage engagement.\n\n"
        "# Lines 9-10: WHY IT MATTERS – Show the impact, value, or relevance\n"
        "# Make it relatable to your audience (developers, recruiters, entrepreneurs, etc.)\n\n"
        "# Lines 11-12: CALL TO ACTION – Encourage replies, shares, or connections\n"
        "# Be conversational and soft with the CTA.\n\n"
        "# Line 13: HASHTAGS – Use 3-5 relevant and specific tags\n"
        "# Avoid generic ones like #motivation or #life\n\n"
        "Return only the enhanced caption following this structure, no explanations or additional text.\n"
        "DO NOT include the section headers or tips in your response, only the actual content.\n\n"
        f"Original caption:\n{caption}"
    )
    
    try:
        enhanced = generate_text(prompt)
        return enhanced.strip()
    except Exception as e:
        print(f"[❌] Caption enhancement error: {e}")
        return caption  # Return original caption if enhancement fails
