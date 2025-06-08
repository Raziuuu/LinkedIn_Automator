# gui/main.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from PIL import Image, ImageTk
from gui.login_tab import LoginTab
from gui.connection_tab import ConnectionTab
from gui.post_tab import PostTab
from gui.message_tab import MessageTab
from gui.feed_tab import FeedTab
from gui.utils import create_tooltip

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class LinkedInAutomatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Automator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Set application icon
        try:
            logo_path = os.path.join(project_root, "assets/logo.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((32, 32), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                self.root.iconphoto(True, logo_photo)
        except Exception as e:
            print(f"Note: Using default icon (logo not found at {logo_path})")

        self.driver = None
        self.is_logged_in = False

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tab frames
        self.login_tab = ttk.Frame(self.notebook)
        self.connection_tab = ttk.Frame(self.notebook)
        self.post_tab = ttk.Frame(self.notebook)
        self.message_tab = ttk.Frame(self.notebook)
        self.feed_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.login_tab, text="Login")
        self.notebook.add(self.connection_tab, text="Connections")
        self.notebook.add(self.post_tab, text="Post")
        self.notebook.add(self.message_tab, text="Messages")
        self.notebook.add(self.feed_tab, text="Feed")

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Not logged in")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize tab modules
        self.login_tab_module = LoginTab(self.login_tab, self)
        self.connection_tab_module = ConnectionTab(self.connection_tab, self)
        self.post_tab_module = PostTab(self.post_tab, self)
        self.message_tab_module = MessageTab(self.message_tab, self)
        self.feed_tab_module = FeedTab(self.feed_tab, self)

    def on_closing(self):
        """Handle window closing event."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing browser: {e}")
        
        # Save any necessary state or cleanup
        try:
            # Add any cleanup code here
            pass
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        # Destroy the root window
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LinkedInAutomatorGUI(root)
    root.mainloop()