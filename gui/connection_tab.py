import tkinter as tk
from tkinter import ttk, messagebox
import threading
from automation.connection_requester import process_connections, reset_counters
from .utils import create_scrollable_frame, create_tooltip

class ConnectionTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.connection_tab_initialized = False
        self.setup_tab()

    def setup_tab(self):
        if self.connection_tab_initialized:
            return
        self.connection_tab_initialized = True

        for widget in self.parent.winfo_children():
            widget.destroy()

        canvas, frame = create_scrollable_frame(self.parent)
        canvas.pack(fill=tk.BOTH, expand=True)

        # 1. Connection Request Settings
        self.config_frame = ttk.LabelFrame(frame, text="Connection Request Settings")
        self.config_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        ttk.Label(self.config_frame, text="Max Connection Requests:").pack(anchor=tk.W, pady=5)
        self.max_requests_var = tk.IntVar(value=5)
        max_requests_spinbox = ttk.Spinbox(self.config_frame, from_=1, to=20, textvariable=self.max_requests_var)
        max_requests_spinbox.pack(fill=tk.X, pady=5, padx=10)
        create_tooltip(max_requests_spinbox, "Maximum number of connection requests to send")

        start_button = ttk.Button(self.config_frame, text="Start Connection Requests", command=self.send_connection_requests)
        start_button.pack(pady=10, fill=tk.X, padx=10)
        create_tooltip(start_button, "Start processing connection requests")

        # 2. Connection Profile (initialize but hide initially)
        self.connection_actions_frame = ttk.LabelFrame(frame, text="Connection Profile")
        self.connection_actions_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        profile_info_frame = ttk.Frame(self.connection_actions_frame)
        profile_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        profile_box = ttk.Frame(profile_info_frame, relief=tk.GROOVE, borderwidth=2)
        profile_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.current_connection_var = tk.StringVar(value="No connections loaded")
        current_connection_label = ttk.Label(profile_box, textvariable=self.current_connection_var,
                                            font=("Arial", 10, "bold"), wraplength=500,
                                            justify=tk.LEFT, padding=(10, 10))
        current_connection_label.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        decision_frame = ttk.Frame(self.connection_actions_frame)
        decision_frame.pack(fill=tk.BOTH, expand=False, pady=5)
        ttk.Label(decision_frame, text="Send request? [y/n/l]:").pack(side=tk.LEFT)
        self.decision_entry = ttk.Entry(decision_frame, width=10)
        self.decision_entry.pack(side=tk.LEFT, padx=5)
        self.decision_button = ttk.Button(decision_frame, text="Submit", command=self.submit_decision)
        self.decision_button.pack(side=tk.LEFT)
        create_tooltip(self.decision_entry, "Enter y (send), n (skip), or l (save for later)")

        button_frame = ttk.Frame(self.connection_actions_frame)
        button_frame.pack(fill=tk.BOTH, expand=False, pady=10)

        self.app.root.style = ttk.Style()
        self.app.root.style.configure('Green.TButton', background='green')

        send_button = ttk.Button(button_frame, text="Send Request ✓", style='Green.TButton',
                                 command=lambda: self.process_connection_action("y"))
        send_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        create_tooltip(send_button, "Send connection request to this person")

        skip_button = ttk.Button(button_frame, text="Skip ✗", command=lambda: self.process_connection_action("n"))
        skip_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        create_tooltip(skip_button, "Skip this connection suggestion")

        save_button = ttk.Button(button_frame, text="Save for Later 📌",
                                 command=lambda: self.process_connection_action("l"))
        save_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        create_tooltip(save_button, "Save this profile for later review")

        self.connection_actions_frame.pack_forget()

        # 3. Connection Progress
        log_frame = ttk.LabelFrame(frame, text="Connection Progress")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.connection_log_text = tk.Text(log_frame, height=15, width=50, wrap=tk.WORD, state='disabled')
        self.connection_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        connection_log_scrollbar = ttk.Scrollbar(log_frame, command=self.connection_log_text.yview)
        connection_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.connection_log_text.config(yscrollcommand=connection_log_scrollbar.set)

        self.connection_log_messages = []

        self.decision_var = tk.StringVar()
        self.running = False

    def connection_log_message(self, message, clear=False, level="info"):
        if level != "user":
            return  # Only show user-level messages

        # Skip logging profile information (messages containing "👤")
        if "👤" in message:
            return

        prefix = "✨ "
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if clear:
            self.connection_log_messages = []

        self.connection_log_messages.append((timestamp, message, level, prefix))

        self.connection_log_text.config(state='normal')

        if clear:
            self.connection_log_text.delete(1.0, tk.END)

        if message:
            formatted_message = f"[{timestamp}] {prefix}{message}\n"
            self.connection_log_text.insert(tk.END, formatted_message)

        self.connection_log_text.see(tk.END)
        self.connection_log_text.config(state='disabled')
        self.app.root.update_idletasks()

    def output_callback(self, message, level="info"):
        self.connection_log_message(message, level=level)
        # Update profile display
        if level == "user" and "👤" in message:
            profile_lines = message.strip().split("\n")
            profile_text = []
            in_profile = False
            for line in profile_lines:
                if "====" in line:
                    in_profile = not in_profile
                    continue
                if in_profile:
                    profile_text.append(line)
            if profile_text:
                self.current_connection_var.set("\n".join(profile_text))
                self.connection_log_message(f"Updated profile display: {profile_text[0]}", level="debug")

    def decision_callback(self):
        self.decision_entry.delete(0, tk.END)
        self.decision_var.set("")
        self.decision_entry.focus_set()
        self.app.root.wait_variable(self.decision_var)
        decision = self.decision_var.get().strip().lower()
        return decision if decision in ['y', 'n', 'l'] else None

    def submit_decision(self):
        decision = self.decision_entry.get().strip().lower()
        if decision in ['y', 'n', 'l']:
            self.decision_var.set(decision)
        else:
            self.output_callback("⚠️ Invalid option. Choose [y/n/l]\n", level="user")

    def process_connection_action(self, action):
        if action in ['y', 'n', 'l']:
            self.decision_entry.delete(0, tk.END)
            self.decision_entry.insert(0, action)
            self.submit_decision()

    def check_login_status(self):
        if not self.app.is_logged_in or not self.app.driver:
            messagebox.showerror("Error", "Please login to LinkedIn first")
            return False
        return True

    def send_connection_requests(self):
        if not self.check_login_status():
            return

        if self.running:
            messagebox.showwarning("Warning", "Connection request process is already running.")
            return

        max_requests = self.max_requests_var.get()

        self.running = True
        reset_counters()

        # Pack the connection_actions_frame in the correct position (after config_frame)
        self.connection_actions_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10, after=self.config_frame)
        self.app.notebook.select(self.parent)

        def connection_process():
            try:
                self.app.status_var.set("Starting connection requests...")
                self.connection_log_message("Starting connection request process...", clear=True, level="user")

                def log_callback(message, level="info"):
                    self.connection_log_message(message, level=level)

                processed_count = process_connections(
                    self.app.driver,
                    max_requests=max_requests,
                    output_callback=self.output_callback,
                    decision_callback=self.decision_callback,
                    counter_callback=None
                )

                if processed_count > 0:
                    self.connection_log_message(
                        f"✅ Processed {processed_count} profiles",
                        level="user"
                    )
                    self.app.root.after(0, lambda: messagebox.showinfo(
                        "Success",
                        f"Connection request process completed. Processed {processed_count} profiles."
                    ))
                    self.app.status_var.set(f"Processed {processed_count} profiles")
                else:
                    self.connection_log_message(
                        "⚠️ No profiles found to process. Check LinkedIn 'My Network' page or try again later.",
                        level="user"
                    )
                    self.app.root.after(0, lambda: messagebox.showwarning(
                        "Warning",
                        "No profiles found to process. Please check the LinkedIn 'My Network' page or try again later."
                    ))
                    self.app.status_var.set("No profiles processed")

            except Exception as e:
                error_message = str(e)
                self.app.status_var.set(f"Error in connection requests: {error_message}")
                self.connection_log_message(f"❌ Error: {error_message}", level="user")
                self.app.root.after(0, lambda msg=error_message: messagebox.showerror("Error", f"An error occurred: {msg}"))
            finally:
                self.running = False
                self.connection_actions_frame.pack_forget()

        threading.Thread(target=connection_process, daemon=True).start()