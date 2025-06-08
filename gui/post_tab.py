# gui/post_tab.py (updated)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import time
from automation.post_creator import create_linkedin_post
from .utils import create_scrollable_frame, create_tooltip

class PostTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_tab()

    def setup_tab(self):
        canvas, frame = create_scrollable_frame(self.parent)
        canvas.pack(fill=tk.BOTH, expand=True)

        post_frame = ttk.LabelFrame(frame, text="Create LinkedIn Post")
        post_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        ttk.Label(post_frame, text="Post Caption:").pack(anchor=tk.W, pady=5)
        self.caption_text = tk.Text(post_frame, height=5, width=50)
        self.caption_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        create_tooltip(self.caption_text, "Enter the text for your LinkedIn post")

        self.use_image_var = tk.BooleanVar(value=False)
        use_image_check = ttk.Checkbutton(post_frame, text="Include Image", variable=self.use_image_var, command=self.toggle_image_selection)
        use_image_check.pack(anchor=tk.W, pady=5)
        create_tooltip(use_image_check, "Check to include an image with your post")

        self.image_frame = ttk.Frame(post_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=False, pady=5)
        self.image_frame.pack_forget()

        self.image_path_var = tk.StringVar()
        ttk.Label(self.image_frame, text="Image Path:").pack(side=tk.LEFT, padx=5)
        image_entry = ttk.Entry(self.image_frame, textvariable=self.image_path_var, width=40)
        image_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        browse_button = ttk.Button(self.image_frame, text="Browse", command=self.browse_image)
        browse_button.pack(side=tk.LEFT, padx=5)
        create_tooltip(browse_button, "Select an image file from your computer")

        self.smart_hashtags_var = tk.BooleanVar(value=True)
        smart_hashtags_check = ttk.Checkbutton(post_frame, text="Use Smart Hashtags", variable=self.smart_hashtags_var)
        smart_hashtags_check.pack(anchor=tk.W, pady=5)
        create_tooltip(smart_hashtags_check, "Automatically generate relevant hashtags for your post")

        log_frame = ttk.LabelFrame(frame, text="AI Enhancement Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        log_filter_frame = ttk.Frame(log_frame)
        log_filter_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        ttk.Label(log_filter_frame, text="Show log level:").pack(side=tk.LEFT, padx=5)
        self.log_level_var = tk.StringVar(value="user")
        log_level_combo = ttk.Combobox(log_filter_frame, textvariable=self.log_level_var, width=15)
        log_level_combo['values'] = ("user", "info", "debug")
        log_level_combo.pack(side=tk.LEFT, padx=5)
        create_tooltip(log_level_combo, "Filter log messages by importance")

        log_level_combo.bind('<<ComboboxSelected>>', self.update_log_display)

        self.log_text = tk.Text(log_frame, height=15, width=50, wrap=tk.WORD, state='disabled')
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)

        self.log_messages = []

        self.enhanced_caption_frame = ttk.Frame(frame, relief=tk.RAISED, borderwidth=3)
        self.enhanced_caption_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        ttk.Label(self.enhanced_caption_frame, text="AI CAPTION REVIEW", font=("Arial", 12, "bold")).pack(side=tk.TOP, padx=5, pady=5)

        response_frame = ttk.Frame(self.enhanced_caption_frame)
        response_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Label(response_frame, text="Use this enhanced caption?").pack(side=tk.LEFT, padx=5)
        accept_button = ttk.Button(response_frame, text="Yes", command=lambda: self.respond_to_enhancement(True))
        accept_button.pack(side=tk.LEFT, padx=5)
        reject_button = ttk.Button(response_frame, text="No", command=lambda: self.respond_to_enhancement(False))
        reject_button.pack(side=tk.LEFT, padx=5)

        self.enhanced_caption_frame.pack_forget()

        post_button = ttk.Button(post_frame, text="Create Post", command=self.create_post)
        post_button.pack(pady=10, fill=tk.X, padx=10)
        create_tooltip(post_button, "Create and publish your LinkedIn post")

    def check_login_status(self):
        if not self.app.is_logged_in or not self.app.driver:
            messagebox.showerror("Error", "Please login to LinkedIn first")
            return False
        return True

    def toggle_image_selection(self):
        if self.use_image_var.get():
            self.image_frame.pack(fill=tk.BOTH, expand=False, pady=5)
        else:
            self.image_frame.pack_forget()

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.image_path_var.set(file_path)

    def respond_to_enhancement(self, accepted):
        self.enhancement_accepted = accepted
        if accepted:
            self.log_message("✅ Enhanced caption accepted", level="user")
        else:
            self.log_message("❌ Enhanced caption rejected", level="user")
        self.enhanced_caption_frame.pack_forget()

    def update_log_display(self, event=None):
        selected_level = self.log_level_var.get()
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        for timestamp, message, level, prefix in self.log_messages:
            show = False
            if selected_level == "debug":
                show = True
            elif selected_level == "info" and level != "debug":
                show = True
            elif selected_level == "user" and level == "user":
                show = True
            if show:
                formatted_message = f"[{timestamp}] {prefix}{message}\n"
                self.log_text.insert(tk.END, formatted_message)
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    def log_message(self, message, clear=False, level="info"):
        if level == "user":
            prefix = "✨ "
        elif level == "debug":
            prefix = "🔍 "
        else:
            prefix = ""

        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if clear:
            self.log_messages = []

        self.log_messages.append((timestamp, message, level, prefix))

        selected_level = self.log_level_var.get()
        show_message = False
        if selected_level == "debug":
            show_message = True
        elif selected_level == "info" and level != "debug":
            show_message = True
        elif selected_level == "user" and level == "user":
            show_message = True

        self.log_text.config(state='normal')

        if clear:
            self.log_text.delete("1.0", tk.END)

        if message and show_message:
            formatted_message = f"[{timestamp}] {prefix}{message}\n"
            self.log_text.insert(tk.END, formatted_message)

        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.app.root.update_idletasks()

    def create_post(self):
        if not self.check_login_status():
            return

        def post_process():
            try:
                caption = self.caption_text.get("1.0", tk.END).strip()
                if not caption:
                    messagebox.showerror("Error", "Please enter a caption for your post")
                    self.app.status_var.set("Post creation cancelled: No caption")
                    return

                image_path = None
                if self.use_image_var.get():
                    image_path = self.image_path_var.get()
                    if not image_path or not os.path.exists(image_path):
                        messagebox.showerror("Error", "Please select a valid image file")
                        self.app.status_var.set("Post creation cancelled: Invalid image")
                        return

                self.app.status_var.set("Creating LinkedIn post...")
                self.log_message("Starting post creation...", clear=True, level="user")

                from ai.ai_generator import enhance_caption, detect_topic_and_hashtags

                def remove_non_bmp(text):
                    return ''.join(char for char in text if ord(char) < 0x10000)

                clean_caption = remove_non_bmp(caption)

                try:
                    self.log_message("Enhancing caption with AI...", level="info")
                    enhanced_caption = enhance_caption(clean_caption)
                    self.log_message(f"AI-generated caption: {enhanced_caption}", level="user")

                    self.caption_text.config(state='normal')
                    self.caption_text.delete("1.0", tk.END)
                    self.caption_text.insert("1.0", enhanced_caption)
                    self.caption_text.config(state='normal')
                    self.enhanced_caption_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

                    self.enhancement_accepted = None
                    while self.enhancement_accepted is None:
                        self.app.root.update()
                        time.sleep(0.1)

                    if not self.enhancement_accepted:
                        self.caption_text.config(state='normal')
                        self.caption_text.delete("1.0", tk.END)
                        self.caption_text.insert("1.0", clean_caption)
                        self.caption_text.config(state='disabled')
                        self.log_message("Reverted to original caption", level="user")

                    final_caption = self.caption_text.get("1.0", tk.END).strip()

                    if self.smart_hashtags_var.get():
                        self.log_message("Generating smart hashtags...", level="info")
                        topic, hashtags = detect_topic_and_hashtags(final_caption)
                        self.log_message(f"Detected Topic: {topic}", level="info")
                        self.log_message(f"Hashtags: {', '.join(hashtags)}", level="info")
                        final_caption += "\n" + " ".join(hashtags)

                    success = create_linkedin_post(self.app.driver, final_caption, image_path)
                    if success:
                        self.log_message("✅ Post created successfully", level="user")
                        self.app.root.after(0, lambda: messagebox.showinfo("Success", "Post created successfully"))
                        self.app.status_var.set("Post created successfully")
                    else:
                        self.log_message("❌ Failed to create post", level="user")
                        self.app.root.after(0, lambda: messagebox.showerror("Error", "Failed to create post"))
                        self.app.status_var.set("Post creation failed")

                except Exception as e:
                    error_message = str(e)
                    self.log_message(f"❌ Error enhancing caption: {error_message}", level="user")
                    self.app.root.after(0, lambda msg=error_message: messagebox.showerror("Error", f"Error enhancing caption: {msg}"))
                    self.app.status_var.set("Post creation failed")

            except Exception as e:
                error_message = str(e)
                self.log_message(f"❌ Error creating post: {error_message}", level="user")
                self.app.root.after(0, lambda msg=error_message: messagebox.showerror("Error", f"An error occurred: {msg}"))
                self.app.status_var.set("Post creation failed")

        threading.Thread(target=post_process, daemon=True).start()