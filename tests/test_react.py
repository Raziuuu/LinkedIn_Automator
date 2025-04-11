# test_react.py (for testing purpose)
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ai.react_planner import get_action_plan

if __name__ == "__main__":
    user_cmd = input("🗣️ What do you want to automate on LinkedIn? ")
    get_action_plan(user_cmd)
