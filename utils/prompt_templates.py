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

# utils/prompt_templates.py

def get_alumni_message_template(
    name,
    college,
    department=None,
    graduation_year=None,
    purpose="connect",
    tone="professional"
):
    message = f"Hi {name},\n\n"

    if tone == "friendly":
        message += f"I'm a recent graduate from {college}"
    else:
        message += f"I’m reaching out as a recent graduate from {college}"

    if department:
        message += f", Department of {department}"
    if graduation_year:
        message += f", Class of {graduation_year}"

    message += ". "

    if purpose == "connect":
        message += "I’d love to connect and learn more about your journey in the industry."
    elif purpose == "mentorship":
        message += "I’m seeking some guidance as I navigate early career opportunities and would appreciate your insights."
    elif purpose == "referral":
        message += "I’m actively exploring roles in your company and was hoping you might be open to a quick chat or a referral."

    message += "\n\nLooking forward to connecting!\nThanks!"
    return message
