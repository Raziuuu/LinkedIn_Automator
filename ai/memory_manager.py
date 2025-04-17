# memory/memory_utils.py

import json
import os

log_path = "logs/message_log.json"

def load_log():
    if not os.path.exists(log_path):
        return {}
    with open(log_path, "r") as f:
        return json.load(f)

def save_log(log):
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)

def has_messaged_before(name):
    log = load_log()
    return name in log

def record_message(name, message):
    log = load_log()
    log[name] = message
    save_log(log)
