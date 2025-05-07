import os
import json
import datetime

# Define the log directory
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Define the log file path
LOG_FILE = os.path.join(LOG_DIR, "action_log.json")

def log_action(action_type, target, details=None):
    """
    Log an action performed by the automation.
    
    Args:
        action_type: Type of action (e.g., "MessageSent", "ConnectionRequested")
        target: Target of the action (e.g., person name, profile URL)
        details: Additional details about the action (optional)
    """
    # Create a new log entry
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "action": action_type,
        "target": target,
        "details": details
    }
    
    # Load existing logs
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted, start with an empty list
            logs = []
    
    # Add the new log entry
    logs.append(log_entry)
    
    # Save the updated logs
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
    
    print(f"✅ Logged action: {action_type} - {target}")
