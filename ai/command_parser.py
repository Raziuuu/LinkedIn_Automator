# ai/command_parser.py

import re

def normalize_command(command):
    return command.lower().strip()

def parse_command(command):
    """
    Returns structured dict: {
        intent: str,
        target: str,
        params: dict
    }
    """
    command = normalize_command(command)

    # 1. Messaging Intent
    if "message" in command or "send a message" in command:
        return {
            "intent": "send_message",
            "target": "recent_connections" if "recent" in command else "unknown",
            "params": {
                "count": int(re.search(r'\d+', command).group()) if re.search(r'\d+', command) else 1
            }
        }

    # 2. Posting Intent
    elif "post" in command:
        return {
            "intent": "post_content",
            "target": "feed",
            "params": {
                "media": "image" if "image" in command else "text",
                "caption": "caption included" if "caption" in command else "no caption"
            }
        }

    # 3. Job Application Intent
    elif "apply" in command:
        return {
            "intent": "apply_jobs",
            "target": "job_listings",
            "params": {
                "criteria": "generic"  # Can be improved using NLP later
            }
        }

    # 4. Fallback
    else:
        return {
            "intent": "unknown",
            "target": "unknown",
            "params": {}
        }
