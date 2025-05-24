#!/usr/bin/env python
import os
import sys
import subprocess

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import tkinter
        import selenium
        import dotenv
        
        # Check specifically for Gemini API
        try:
            import google.generativeai as genai
            
            # Check if API key is configured in .env
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("[⚠️] Warning: GEMINI_API_KEY not found in environment variables.")
                print("    AI features like smart hashtags and caption enhancement will not work.")
                print("    Create a .env file with your GEMINI_API_KEY to enable these features.")
                print("    You can get an API key from: https://aistudio.google.com/app/apikey")
                
        except ImportError:
            print("[⚠️] Warning: Google Generative AI package not found.")
            print("    AI features will not be available.")
            return False
            
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Please install them manually.")
        return False

def main():
    """Main function to start the application"""
    # Check dependencies
    if not check_dependencies():
        user_input = input("Would you like to install the required dependencies? (y/n): ")
        if user_input.lower() == 'y':
            if not install_dependencies():
                return
        else:
            print("Please install the required dependencies and try again.")
            return
    
    # Add project root to path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Import and run GUI
    try:
        from gui.run_gui import main as run_gui
        run_gui()
    except Exception as e:
        print(f"Error starting the application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 