import os
import sys

# Add the project root directory to the Python path
script_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_path)
sys.path.insert(0, project_root)

from gui.main import LinkedInAutomatorGUI
import tkinter as tk

def main():
    root = tk.Tk()
    app = LinkedInAutomatorGUI(root)
    
    # Set up window closing protocol
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main() 