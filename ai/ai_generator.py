# import requests

# def generate_content(prompt):
#     response = requests.post(
#         "http://localhost:11434/api/generate",
#         json={"model": "mistral", "prompt": prompt, "stream": False}
#     )
#     return response.json()['response']

# if __name__ == "__main__":
#     output = generate_content("Write a friendly connection request message.")
#     print("[AI GENERATED]:", output)

# ai_generator.py

import requests
import sys

def generate_ai_steps(prompt: str) -> str:
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()['response']
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Ollama server. Please make sure it's running on port 11434.")
        print("   You can start it by running: ollama serve")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: An error occurred while making the request: {str(e)}")
        sys.exit(1)
    except KeyError:
        print("❌ Error: Unexpected response format from Ollama server.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: An unexpected error occurred: {str(e)}")
        sys.exit(1)
