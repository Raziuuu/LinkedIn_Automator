# LinkedIn Automator GUI

A graphical user interface for automating various LinkedIn tasks.

## Features

- **Login to LinkedIn**: Authenticate with your LinkedIn credentials
- **Send Connection Requests**: Automatically send connection requests to recommended users
- **Create LinkedIn Posts**: Create posts with optional images and smart hashtags
  - Uses AI to format your posts with a professional structure
  - Generates relevant, industry-specific hashtags
- **Send Messages**: Send bulk messages to your LinkedIn connections
- **Feed Interaction**: Scroll through your feed and interact with posts (like, comment)

## Post Structure

When you create a post, the AI will automatically format it according to this professional structure:

1. **HOOK** (Lines 1-2): Attention-grabbing opener to make readers stop scrolling
2. **CONTEXT** (Lines 3-6): Explanation of what you're sharing and its value
3. **CHALLENGE/PERSONAL TOUCH** (Lines 7-8): Authentic insight into challenges or learnings
4. **WHY IT MATTERS** (Lines 9-10): Relevance and impact for your audience
5. **CALL TO ACTION** (Lines 11-12): Engagement prompt encouraging interaction
6. **HASHTAGS** (Line 13): 3-5 relevant and specific tags

This structure is based on best practices for LinkedIn content to maximize engagement.

## Setup and Installation

1. Make sure you have Python installed (Python 3.7+ recommended)
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up your credentials by creating a `.env` file in the project root with:
   ```
   # LinkedIn credentials
   LINKEDIN_USERNAME=your_email@example.com
   LINKEDIN_PASSWORD=your_password
   
   # Gemini API key for AI features (get from https://aistudio.google.com/app/apikey)
   GEMINI_API_KEY=your_gemini_api_key
   ```

## Usage

1. Run the GUI application:
   ```
   python gui/run_gui.py
   ```
   
2. The application will open with the following tabs:
   - **Login**: Authenticate with LinkedIn
   - **Connections**: Send connection requests
   - **Post**: Create LinkedIn posts
   - **Messages**: Send bulk messages
   - **Feed**: Interact with your feed

3. Always start by logging in from the Login tab before using other features.

## Notes

- The browser window will open for all operations. Do not close it while tasks are running.
- Some interactions may require your attention during automation.
- Use responsibly and in accordance with LinkedIn's terms of service.
- The smart hashtags and caption enhancement features require a valid Gemini API key.

## Troubleshooting

- If login fails, ensure your credentials are correct in the `.env` file.
- If AI features aren't working, verify your Gemini API key is valid and properly set in the `.env` file.
- If automation fails, try restarting the application and logging in again.
- For persistent issues, check that your LinkedIn account is not restricted due to automation. 