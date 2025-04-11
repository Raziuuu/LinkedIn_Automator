# utils/prompt_templates.py

def get_react_prompt(user_command: str) -> str:
    return f"""
You are a LinkedIn Automation Assistant using the ReAct (Reason + Act) pattern.

Given this user command:
"{user_command}"

Break it down into 3-6 clear, numbered steps that a browser automation tool can perform.
Only include what is needed. Be clear and concise.

After the steps, ask:
"Do you want to proceed? (yes / no / modify / retry)"
"""
