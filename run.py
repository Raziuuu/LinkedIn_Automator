import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gui.main import LinkedInAutomator

if __name__ == "__main__":
    app = LinkedInAutomator()
    app.root.mainloop() 