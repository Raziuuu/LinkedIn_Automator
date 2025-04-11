# test_parser.py (for testing purpose)
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ai.command_parser import parse_command

commands = [
    "Send a message to my 5 recent connections",
    "Post an image with caption",
    "Apply to jobs"
]

for cmd in commands:
    print(f"\nCommand: {cmd}")
    print("Parsed Output:", parse_command(cmd))


