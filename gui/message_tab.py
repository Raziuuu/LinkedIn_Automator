import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from automation.message_bot import open_messaging_page, send_message, get_contacts
from .utils import create_scrollable_frame, create_tooltip
import os

class MessageTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_tab()

    def setup_tab(self):
        canvas, frame = create_scrollable_frame(self.parent)
        canvas.pack(fill=tk.BOTH, expand=True)

        # 1. Message Configuration
        config_frame = ttk.LabelFrame(frame, text="Message Configuration")
        config_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        ttk.Label(config_frame, text="Messaging Mode:").pack(anchor=tk.W, pady=5)
        self.message_mode_var = tk.StringVar(value="specific")
        mode_frame = ttk.Frame(config_frame)
        mode_frame.pack(fill=tk.BOTH, expand=False, pady=5)

        ttk.Radiobutton(mode_frame, text="Broadcast to recent contacts",
                        variable=self.message_mode_var, value="broadcast").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Select specific contacts",
                        variable=self.message_mode_var, value="specific").pack(side=tk.LEFT, padx=10)

        ttk.Label(config_frame, text="Message Tone:").pack(anchor=tk.W, pady=5)
        self.message_tone_var = tk.StringVar(value="professional")
        tone_frame = ttk.Frame(config_frame)
        tone_frame.pack(fill=tk.BOTH, expand=False, pady=5)

        ttk.Radiobutton(tone_frame, text="Professional",
                        variable=self.message_tone_var, value="professional").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(tone_frame, text="Friendly",
                        variable=self.message_tone_var, value="friendly").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(tone_frame, text="Casual",
                        variable=self.message_tone_var, value="casual").pack(side=tk.LEFT, padx=10)

        # 2. Contact Selection
        self.contacts_frame = ttk.LabelFrame(frame, text="Contact Selection")
        self.contacts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        load_contacts_button = ttk.Button(self.contacts_frame, text="Load Recent Contacts",
                                          command=self.load_recent_contacts)
        load_contacts_button.pack(pady=10, fill=tk.X, padx=10)

        self.contacts_listbox_frame = ttk.Frame(self.contacts_frame)
        self.contacts_listbox_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(self.contacts_listbox_frame, text="Select contacts to message:").pack(anchor=tk.W)

        listbox_frame = ttk.Frame(self.contacts_listbox_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.contacts_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, height=10)
        self.contacts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        contacts_scrollbar = ttk.Scrollbar(listbox_frame, command=self.contacts_listbox.yview)
        contacts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.contacts_listbox.config(yscrollcommand=contacts_scrollbar.set)

        self.contacts_listbox_frame.pack_forget()

        self.contacts_data = []

        # 3. Message Content
        self.topic_frame = ttk.LabelFrame(frame, text="Message Content")
        self.topic_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        instruction_text = "Enter what you want to talk about. AI will create a personalized message based on this input."
        instruction_label = ttk.Label(self.topic_frame, text=instruction_text, wraplength=600)
        instruction_label.pack(anchor=tk.W, pady=5)

        ttk.Label(self.topic_frame, text="Your message topic or context:").pack(anchor=tk.W, pady=5)
        self.topic_text = tk.Text(self.topic_frame, height=4, width=50)
        self.topic_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        create_tooltip(self.topic_text, "Describe what you want to talk about. AI will create a message based on this.")

        example_text = "Example: I'd like to discuss potential collaboration on AI projects in the healthcare sector."
        example_label = ttk.Label(self.topic_frame, text=example_text, font=("Arial", 9, "italic"), foreground="gray")
        example_label.pack(anchor=tk.W, pady=5)

        self.use_resume_var = tk.BooleanVar(value=False)
        use_resume_check = ttk.Checkbutton(self.topic_frame, text="Attach Resume", variable=self.use_resume_var,
                                          command=self.toggle_resume_selection)
        use_resume_check.pack(anchor=tk.W, pady=5)
        create_tooltip(use_resume_check, "Check to attach a resume with your message")

        self.resume_frame = ttk.Frame(self.topic_frame)
        self.resume_frame.pack(fill=tk.BOTH, expand=False, pady=5)
        self.resume_frame.pack_forget()

        self.resume_path_var = tk.StringVar()
        ttk.Label(self.resume_frame, text="Resume Path:").pack(side=tk.LEFT, padx=5)
        resume_entry = ttk.Entry(self.resume_frame, textvariable=self.resume_path_var, width=40)
        resume_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        browse_button = ttk.Button(self.resume_frame, text="Browse", command=self.browse_resume)
        browse_button.pack(side=tk.LEFT, padx=5)
        create_tooltip(browse_button, "Select a resume file (PDF) from your computer")

        self.topic_frame.pack_forget()

        # 4. AI Generated Message
        message_preview_frame = ttk.LabelFrame(frame, text="AI Generated Message")
        message_preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        preview_button = ttk.Button(message_preview_frame, text="Generate Message with AI",
                                    command=self.generate_message_preview)
        preview_button.pack(pady=10, fill=tk.X, padx=10)
        create_tooltip(preview_button, "Generate a personalized message based on your topic and selected tone")

        self.message_preview_text = tk.Text(message_preview_frame, height=10, width=50, state='disabled')
        self.message_preview_text.pack(fill=tk.BOTH, expand=True, pady=5)

        edit_button = ttk.Button(message_preview_frame, text="Edit Message", command=self.edit_message_template)
        edit_button.pack(pady=10, fill=tk.X, padx=10)
        create_tooltip(edit_button, "Customize the AI-generated message")

        # 5. Messaging Log (with Send Messages button)
        log_frame = ttk.LabelFrame(frame, text="Messaging Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        send_frame = ttk.Frame(log_frame)
        send_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

        send_button = ttk.Button(send_frame, text="Send Messages", command=self.start_messaging)
        send_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        create_tooltip(send_button, "Start sending messages to selected contacts")

        log_filter_frame = ttk.Frame(log_frame)
        log_filter_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        ttk.Label(log_filter_frame, text="Show log level:").pack(side=tk.LEFT, padx=5)
        self.messaging_log_level_var = tk.StringVar(value="user")
        messaging_log_level_combo = ttk.Combobox(log_filter_frame, textvariable=self.messaging_log_level_var, width=15)
        messaging_log_level_combo['values'] = ("user", "info", "debug")
        messaging_log_level_combo.pack(side=tk.LEFT, padx=5)
        create_tooltip(messaging_log_level_combo, "Filter log messages by importance")

        messaging_log_level_combo.bind('<<ComboboxSelected>>', self.update_messaging_log_display)

        self.messaging_log_text = tk.Text(log_frame, height=10, width=50, wrap=tk.WORD, state='disabled')
        self.messaging_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        messaging_log_scrollbar = ttk.Scrollbar(log_frame, command=self.messaging_log_text.yview)
        messaging_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.messaging_log_text.config(yscrollcommand=messaging_log_scrollbar.set)

        self.messaging_log_messages = []

    def check_login_status(self):
        if not self.app.is_logged_in or not self.app.driver:
            messagebox.showerror("Error", "Please login to LinkedIn first")
            return False
        return True

    def load_recent_contacts(self):
        if not self.check_login_status():
            return

        self.messaging_log_message("Loading recent contacts...", clear=True, level="user")

        def load_contacts_process():
            try:
                self.messaging_log_message("Opening LinkedIn messaging page...", level="info")
                open_messaging_page(self.app.driver)

                self.messaging_log_message("Finding recent conversations...", level="info")
                contacts = get_contacts(self.app.driver)

                if not contacts:
                    self.messaging_log_message(
                        "⚠️ No recent contacts found. This could be because:\n"
                        "- Your LinkedIn messaging inbox is empty. Try sending a message manually on LinkedIn to populate your conversation list.\n"
                        "- LinkedIn's page structure has changed, or the page failed to load correctly.\n"
                        "Please check the console logs for more details.",
                        level="user"
                    )
                    return

                self.contacts_data = contacts
                self.app.root.after(0, self.update_contacts_listbox, contacts)

                self.messaging_log_message(f"Found {len(contacts)} recent contacts", level="user")
            except Exception as e:
                error_message = str(e)
                self.messaging_log_message(f"Error loading contacts: {error_message}", level="error")

        threading.Thread(target=load_contacts_process, daemon=True).start()

    def update_contacts_listbox(self, contacts):
        self.contacts_listbox.delete(0, tk.END)

        for name, _ in contacts:
            self.contacts_listbox.insert(tk.END, name)

        self.contacts_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.topic_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10, after=self.contacts_frame)

        self.messaging_log_message("✅ Contacts loaded successfully.", level="user")
        self.messaging_log_message("👉 Select contacts and enter a message topic, then click 'Generate Message Preview'", level="user")

    def generate_message_preview(self):
        if not self.contacts_data:
            messagebox.showerror("Error", "Please load contacts first")
            return

        tone = self.message_tone_var.get()
        topic = self.topic_text.get("1.0", tk.END).strip()
        if not topic:
            messagebox.showerror("Error", "Please enter a topic or context for your message")
            return

        self.messaging_log_message("Generating message preview...", level="user")

        try:
            self.messaging_log_message("Creating message with AI...", level="info")
            from ai.ai_generator import generate_text

            selected_indices = self.contacts_listbox.curselection()
            recipient_name = "{name}"
            if selected_indices and self.message_mode_var.get() == "specific":
                first_index = selected_indices[0]
                if first_index < len(self.contacts_data):
                    recipient_name = self.contacts_data[first_index][0]

            prompt = f"""
            Create a LinkedIn message about this topic: '{topic}'
            
            Rules:
            1. Keep the message under 400 characters
            2. Use a {tone} tone
            3. Address the recipient as {recipient_name}
            4. Start with an engaging hook related to the topic
            5. Acknowledge the recipient's role or company without needing specific details
            6. Include a clear call to action for a referral or conversation
            7. Mention that a resume is attached if applicable
            8. DO NOT use greetings like 'Hi {recipient_name}, I came across your profile'
            9. Vary phrasing slightly based on tone
            
            Example for topic 'Java Developer', professional tone:
            {recipient_name}, I'm excited about Java development and admire the innovative work at your company. Given your role, could you kindly consider referring me or sharing insights? I've attached my resume and would love to chat further!
            
            Return only the message text.
            """

            message = generate_text(prompt)

            if message:
                message = message.strip('"\'')
                self.message_preview_text.config(state='normal')
                self.message_preview_text.delete("1.0", tk.END)
                self.message_preview_text.insert(tk.END, message)
                self.message_preview_text.config(state='disabled')

                self.messaging_log_message("✅ Preview message generated with AI", level="user")
            else:
                self.message_preview_text.config(state='normal')
                self.message_preview_text.delete("1.0", tk.END)
                simple_message = f"{recipient_name}, I'm interested in {topic}. Could we discuss this? I've attached my resume."
                self.message_preview_text.insert(tk.END, simple_message)
                self.message_preview_text.config(state='disabled')

                self.messaging_log_message("⚠️ Could not generate message with AI, using default message", level="user")

        except Exception as e:
            error_message = str(e)
            self.messaging_log_message(f"Failed to generate message: {error_message}", level="user")
            self.message_preview_text.config(state='normal')
            self.message_preview_text.delete("1.0", tk.END)
            simple_message = f"{recipient_name}, I'm interested in {topic}. Could we discuss this? I've attached my resume."
            self.message_preview_text.insert(tk.END, simple_message)
            self.message_preview_text.config(state='disabled')

    def edit_message_template(self):
        self.message_preview_text.config(state='normal')
        self.messaging_log_message("You can now edit the message template", level="info")

    def toggle_resume_selection(self):
        if self.use_resume_var.get():
            self.resume_frame.pack(fill=tk.BOTH, expand=False, pady=5)
        else:
            self.resume_frame.pack_forget()

    def browse_resume(self):
        file_path = filedialog.askopenfilename(
            title="Select a resume",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            self.resume_path_var.set(file_path)

    def messaging_log_message(self, message, clear=False, level="info"):
        if level == "user":
            prefix = "✨ "
        elif level == "debug":
            prefix = "🔍 "
        else:
            prefix = ""

        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if clear:
            self.messaging_log_messages = []

        self.messaging_log_messages.append((timestamp, message, level, prefix))

        selected_level = self.messaging_log_level_var.get()
        show_message = False
        if selected_level == "debug":
            show_message = True
        elif selected_level == "info" and level != "debug":
            show_message = True
        elif selected_level == "user" and level == "user":
            show_message = True

        self.messaging_log_text.config(state='normal')

        if clear:
            self.messaging_log_text.delete(1.0, tk.END)

        if message and show_message:
            formatted_message = f"[{timestamp}] {prefix}{message}\n"
            self.messaging_log_text.insert(tk.END, formatted_message)

        self.messaging_log_text.see(tk.END)
        self.messaging_log_text.config(state='disabled')
        self.app.root.update_idletasks()

    def update_messaging_log_display(self, event=None):
        selected_level = self.messaging_log_level_var.get()

        self.messaging_log_text.config(state='normal')
        self.messaging_log_text.delete(1.0, tk.END)

        for timestamp, message, level, prefix in self.messaging_log_messages:
            show = False
            if selected_level == "debug":
                show = True
            elif selected_level == "info" and level != "debug":
                show = True
            elif selected_level == "user" and level == "user":
                show = True

            if show:
                formatted_message = f"[{timestamp}] {prefix}{message}\n"
                self.messaging_log_text.insert(tk.END, formatted_message)

        self.messaging_log_text.config(state='disabled')
        self.messaging_log_text.see(tk.END)

    def start_messaging(self):
        if not self.check_login_status():
            return

        def messaging_process():
            try:
                topic = self.topic_text.get("1.0", tk.END).strip()
                if not topic:
                    messagebox.showerror("Error", "Please enter a topic or context for your message")
                    self.app.status_var.set("Messaging canceled: No topic")
                    return

                message_template = self.message_preview_text.get("1.0", tk.END).strip()
                if not message_template:
                    messagebox.showerror("Error", "Please generate a message template first")
                    self.app.status_var.set("Messaging canceled: No message template")
                    return

                resume_path = None
                if self.use_resume_var.get():
                    resume_path = self.resume_path_var.get()
                    if not resume_path or not os.path.exists(resume_path):
                        messagebox.showerror("Error", "Please select a valid resume file")
                        self.app.status_var.set("Messaging canceled: Invalid resume")
                        return

                mode = self.message_mode_var.get()
                tone = self.message_tone_var.get()

                self.messaging_log_message("Starting messaging process...", clear=True, level="user")
                self.app.status_var.set("Starting messaging...")

                if mode == "specific":
                    selected_indices = self.contacts_listbox.curselection()
                    if not selected_indices:
                        messagebox.showerror("Error", "Please select at least one contact")
                        self.app.status_var.set("Messaging canceled: No contacts selected")
                        return

                    contacts = [(self.contacts_data[i][0], self.contacts_data[i][1]) for i in selected_indices]
                else:
                    contacts = self.contacts_data

                self.messaging_log_message(f"[debug] Contacts to message: {contacts}", level="debug")

                for name, profile_url in contacts:
                    if not isinstance(name, str):
                        self.messaging_log_message(f"[error] Invalid name type for contact: {type(name)}", level="user")
                        continue

                    self.messaging_log_message(f"Processing message for {name}...", level="user")
                    message = message_template.replace("{name}", name)

                    success = send_message(self.app.driver, name, profile_url, message, resume_path, log_callback=self.messaging_log_message)
                    if success:
                        self.messaging_log_message(f"✅ Message sent to {name}", level="user")
                    else:
                        self.messaging_log_message(f"❌ Failed to send message to {name}", level="user")

                self.messaging_log_message("✅ Messaging completed", level="user")
                self.app.root.after(0, lambda: messagebox.showinfo("Success", "Messaging completed"))
                self.app.status_var.set("Messaging completed")

            except Exception as e:
                error_message = str(e)
                self.messaging_log_message(f"❌ Error: {error_message}", level="user")
                self.app.root.after(0, lambda msg=error_message: messagebox.showerror("Error", f"An error occurred: {msg}"))
                self.app.status_var.set("Messaging failed")

        threading.Thread(target=messaging_process, daemon=True).start()