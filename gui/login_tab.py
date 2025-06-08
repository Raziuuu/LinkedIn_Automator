import tkinter as tk
from tkinter import ttk, messagebox
import threading
from automation.linkedin_automation import create_driver, load_credentials, login_linkedin
from .utils import create_tooltip, create_scrollable_frame
from PIL import Image, ImageTk

class LoginTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_tab()

    def setup_tab(self):
        # Main container with scrollable frame
        outer_frame, frame = create_scrollable_frame(self.parent)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main frame for content (no LabelFrame border to keep it clean)
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Logo at the top center
        try:
            logo_img = Image.open("assets/logo.png")
            logo_img = logo_img.resize((100, 100), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = ttk.Label(main_frame, image=self.logo_photo)
            logo_label.pack(pady=(20, 10))  # Padding above and below the logo
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback if logo fails to load
            logo_label = ttk.Label(main_frame, text="LinkedIn Automator", font=("Helvetica", 16, "bold"))
            logo_label.pack(pady=(20, 10))

        # Login status indicator
        self.login_status_var = tk.StringVar()
        self.login_status_var.set("Not logged in")
        status_label = ttk.Label(
            main_frame,
            textvariable=self.login_status_var,
            font=("Helvetica", 14, "bold"),
            foreground="#ffffff",  # White text
            background="#0077b5",  # LinkedIn blue background
            padding=(10, 5)  # Padding for the label
        )
        status_label.pack(pady=15, fill=tk.X, padx=50)  # Centered with padding

        # Button styling
        button_style = ttk.Style()
        button_style.configure(
            "Custom.TButton",
            font=("Helvetica", 12, "bold"),
            padding=10,
            background="#0077b5",  # LinkedIn blue
            foreground="#000000"   # Black text for better visibility
        )
        # Hover effect
        button_style.map(
            "Custom.TButton",
            background=[("active", "#005f99")],  # Darker blue on hover
            foreground=[("active", "#000000")]   # Keep text black on hover
        )

        # Button container to center buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # Login button
        login_button = ttk.Button(
            button_frame,
            text="Login to LinkedIn",
            command=self.login_to_linkedin,
            style="Custom.TButton"
        )
        login_button.pack(pady=10, padx=50, fill=tk.X)  # Centered with padding
        create_tooltip(login_button, "Login to your LinkedIn account using saved credentials")

        # Logout button
        logout_button = ttk.Button(
            button_frame,
            text="Logout",
            command=self.logout_from_linkedin,
            style="Custom.TButton"
        )
        logout_button.pack(pady=10, padx=50, fill=tk.X)  # Centered with padding
        create_tooltip(logout_button, "Close browser and log out from LinkedIn")

    def login_to_linkedin(self):
        def login_process():
            try:
                self.app.status_var.set("Loading credentials...")
                self.app.root.update_idletasks()

                creds = load_credentials()

                self.app.status_var.set("Creating browser driver...")
                self.app.root.update_idletasks()

                self.app.driver = create_driver()

                self.app.status_var.set("Logging in to LinkedIn...")
                self.app.root.update_idletasks()

                success = login_linkedin(self.app.driver, creds["username"], creds["password"])

                if success:
                    self.app.is_logged_in = True
                    self.app.status_var.set("Logged in successfully")
                    self.login_status_var.set("Logged in as: " + creds["username"])
                else:
                    self.app.status_var.set("Login failed")
                    self.login_status_var.set("Login failed")
                    if self.app.driver:
                        self.app.driver.quit()
                        self.app.driver = None
            except Exception as e:
                self.app.status_var.set(f"Error: {str(e)}")
                self.login_status_var.set("Login error")
                if self.app.driver:
                    self.app.driver.quit()
                    self.app.driver = None

        threading.Thread(target=login_process, daemon=True).start()

    def logout_from_linkedin(self):
        if self.app.driver:
            self.app.driver.quit()
            self.app.driver = None
            self.app.is_logged_in = False
            self.app.status_var.set("Logged out")
            self.login_status_var.set("Not logged in")