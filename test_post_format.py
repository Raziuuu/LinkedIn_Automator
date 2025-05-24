#!/usr/bin/env python
"""
Test script to verify the LinkedIn post formatting with Gemini API
"""
import os
from dotenv import load_dotenv

# Add the project root directory to the Python path
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from ai.ai_generator import enhance_caption, suggest_hashtags

def test_post_formatting():
    print("Testing LinkedIn post formatting...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if Gemini API key is set
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please add your API key to the .env file:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    
    # Sample caption to enhance
    sample_caption = (
        "I'm excited to share that I just completed a LinkedIn automation project! "
        "It uses Selenium for browser automation and has features for posting, "
        "messaging, and connection requests. A great way to streamline LinkedIn management."
    )
    
    # Test caption enhancement
    try:
        print("\n📝 Original Caption:")
        print(sample_caption)
        
        print("\n⏳ Enhancing caption with the new format...")
        enhanced = enhance_caption(sample_caption)
        
        print("\n✨ Enhanced Caption:")
        print(enhanced)
        
        # Test hashtag generation
        print("\n⏳ Generating relevant hashtags...")
        hashtags = suggest_hashtags("LinkedIn automation tool")
        
        print("\n#️⃣ Suggested Hashtags:")
        print(" ".join(hashtags))
        
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    if test_post_formatting():
        print("\n🎉 LinkedIn post formatting test completed successfully!")
    else:
        print("\n❌ LinkedIn post formatting test failed. Please check the errors above.") 