import requests
import sys

def generate_content(prompt):
    """Generate content using local Ollama API with the Mistral model"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        return response.json().get('response', '').strip()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Ollama server. Make sure it's running.")
        return ""
    except Exception as e:
        print(f"❌ Error generating content: {e}")
        return ""

def generate_connection_message(prompt):
    """Generate a personalized connection message"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False}
        )
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"[AI Error] {e}")
        return "Hi! I'd like to connect with you on LinkedIn."

def generate_connection_note(name, headline=None, university=None, company=None):
    """Generate a personalized connection note based on the provided details."""
    # Base note
    note = f"Hi {name},\n\n"

    # Add headline if available
    if headline:
        note += f"I came across your profile and noticed your work as a {headline}.\n"

    # Add university if available
    if university:
        note += f"I see you attended {university}, which is impressive!\n"

    # Add company if available
    if company:
        note += f"Your experience at {company} sounds fascinating.\n"

    # Closing
    note += "\nLooking forward to connecting!"
    return note

def suggest_hashtags(caption):
    """Suggest relevant hashtags for a LinkedIn post"""
    prompt = f"Suggest 5 relevant, trending LinkedIn hashtags for this post:\n\n\"{caption}\""
    response = generate_content(prompt)
    
    # Parse hashtags from response
    hashtags = []
    for word in response.split():
        # Clean up the word and check if it's a hashtag
        cleaned = word.strip(",.!?()[]{}:;\"'")
        if cleaned.startswith("#"):
            hashtags.append(cleaned)
        # If it's a word without a hashtag but looks like it should be one, add the hashtag
        elif len(cleaned) > 2 and cleaned[0].isalpha() and "#" not in cleaned:
            if not any(tag.lower() == f"#{cleaned.lower()}" for tag in hashtags):
                hashtags.append(f"#{cleaned}")
    
    # Fallback if no hashtags were found or AI failed
    if not hashtags:
        return ["#LinkedIn", "#Networking", "#ProfessionalDevelopment", "#CareerGrowth", "#Innovation"]
    
    # Return up to 5 hashtags
    return hashtags[:5]