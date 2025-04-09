import requests

def generate_content(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt, "stream": False}
    )
    return response.json()['response']

if __name__ == "__main__":
    output = generate_content("Write a friendly connection request message.")
    print("[AI GENERATED]:", output)
