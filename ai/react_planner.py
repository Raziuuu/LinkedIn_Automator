# react_planner.py

from ai.ai_generator import generate_ai_steps
from utils.prompt_templates import get_react_prompt

def get_action_plan(user_command):
    react_prompt = get_react_prompt(user_command)
    response = generate_ai_steps(react_prompt)
    
    print("\n🤖 AI Proposed Action Plan:\n")
    print(response.strip())
    
    while True:
        user_input = input("\n🟩 Proceed with these steps? (yes / no / modify / retry): ").lower()
        if user_input == "yes":
            print("✅ Steps confirmed. Proceeding to execution phase...")
            return response
        elif user_input == "no":
            print("❌ Aborting action.")
            return None
        elif user_input == "modify":
            new_command = input("✏️ Enter your modified command: ")
            return get_action_plan(new_command)
        elif user_input == "retry":
            return get_action_plan(user_command)
        else:
            print("⚠️ Invalid input. Try again.")
