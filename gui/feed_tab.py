# gui/feed_tab.py (unchanged from your provided version)
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from queue import Queue
from automation.feed_scroller import engage_feed
from .utils import create_scrollable_frame, create_tooltip
from PIL import Image, ImageTk

class FeedTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_tab()
        self.action_queue = Queue()

    def setup_tab(self):
        canvas, frame = create_scrollable_frame(self.parent)
        canvas.pack(fill=tk.BOTH, expand=True)

        config_frame = ttk.LabelFrame(frame, text="Feed Interaction")
        config_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        info_text = "Interact with LinkedIn posts by liking, commenting, or skipping. AI will summarize each post."
        info_label = ttk.Label(config_frame, text=info_text, wraplength=600)
        info_label.pack(pady=10, fill=tk.X)

        ttk.Label(config_frame, text="Max Posts to Interact With:").pack(anchor=tk.W, pady=5)
        self.max_posts_var = tk.IntVar(value=5)
        max_posts_spinbox = ttk.Spinbox(config_frame, from_=1, to=20, textvariable=self.max_posts_var)
        max_posts_spinbox.pack(fill=tk.X, pady=5, padx=10)
        create_tooltip(max_posts_spinbox, "Maximum number of posts to scroll through and interact with")

        feed_button = ttk.Button(config_frame, text="Start Feed Interaction", command=self.start_feed_interaction)
        feed_button.pack(pady=10, fill=tk.X, padx=10)
        create_tooltip(feed_button, "Start scrolling through your feed and interacting with posts")

        log_frame = ttk.LabelFrame(frame, text="Feed Interaction Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        log_filter_frame = ttk.Frame(log_frame)
        log_filter_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        ttk.Label(log_filter_frame, text="Show log level:").pack(side=tk.LEFT, padx=5)
        self.feed_log_level_var = tk.StringVar(value="user")
        feed_log_level_combo = ttk.Combobox(log_filter_frame, textvariable=self.feed_log_level_var, width=15)
        feed_log_level_combo['values'] = ("user", "info", "debug")
        feed_log_level_combo.pack(side=tk.LEFT, padx=5)
        create_tooltip(feed_log_level_combo, "Filter log messages by importance")

        feed_log_level_combo.bind('<<ComboboxSelected>>', self.update_feed_log_display)

        self.feed_log_text = tk.Text(log_frame, height=15, width=50, wrap=tk.WORD, state='disabled')
        self.feed_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        feed_log_scrollbar = ttk.Scrollbar(log_frame, command=self.feed_log_text.yview)
        feed_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.feed_log_text.config(yscrollcommand=feed_log_scrollbar.set)

        self.feed_log_messages = []

    def check_login_status(self):
        if not self.app.is_logged_in or not self.app.driver:
            messagebox.showerror("Error", "Please login to LinkedIn first")
            return False
        return True

    def update_feed_log_display(self, event=None):
        selected_level = self.feed_log_level_var.get()

        self.feed_log_text.config(state='normal')
        self.feed_log_text.delete(1.0, tk.END)

        for timestamp, message, level, prefix in self.feed_log_messages:
            show = False
            if selected_level == "debug":
                show = True
            elif selected_level == "info" and level != "debug":
                show = True
            elif selected_level == "user" and level == "user":
                show = True

            if show:
                formatted_message = f"[{timestamp}] {prefix}{message}\n"
                self.feed_log_text.insert(tk.END, formatted_message)

        self.feed_log_text.config(state='disabled')
        self.feed_log_text.see(tk.END)

    def feed_log_message(self, message, clear=False, level="info"):
        if level == "user":
            prefix = "✨ "
        elif level == "debug":
            prefix = "🔍 "
        else:
            prefix = ""

        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if clear:
            self.feed_log_messages = []

        self.feed_log_messages.append((timestamp, message, level, prefix))

        selected_level = self.feed_log_level_var.get()
        show_message = False
        if selected_level == "debug":
            show_message = True
        elif selected_level == "info" and level != "debug":
            show_message = True
        elif selected_level == "user" and level == "user":
            show_message = True

        self.feed_log_text.config(state='normal')

        if clear:
            self.feed_log_text.delete("1.0", tk.END)

        if message and show_message:
            formatted_message = f"[{timestamp}] {prefix}{message}\n"
            self.feed_log_text.insert(tk.END, formatted_message)

        self.feed_log_text.see(tk.END)
        self.feed_log_text.config(state='disabled')
        self.app.root.update_idletasks()

    def get_action_input(self, summary, post_index, author_name):
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Post {post_index} Action")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        logo_path = "assets/logo.png"
        try:
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((32, 32), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            dialog.iconphoto(True, logo_photo)
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"Posted by: {author_name}", font=("Arial", 10, "italic")).pack(anchor=tk.W, pady=2)
        
        ttk.Label(frame, text=f"Post {post_index} Summary:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        summary_text = tk.Text(frame, height=6, width=50, wrap=tk.WORD, state=tk.NORMAL)
        summary_text.insert(tk.END, summary)
        summary_text.config(state=tk.DISABLED)
        summary_text.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text="Action:", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        action_var = tk.StringVar(value="")
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(action_frame, text="Like", value="like", variable=action_var).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(action_frame, text="Comment", value="comment", variable=action_var).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(action_frame, text="Skip", value="skip", variable=action_var).pack(side=tk.LEFT, padx=10)
        
        comment_frame = ttk.Frame(frame)
        comment_frame.pack(fill=tk.X, pady=5)
        ttk.Label(comment_frame, text="Comment (if selected):").pack(anchor=tk.W)
        comment_text = tk.Text(comment_frame, height=3, width=50)
        comment_text.pack(fill=tk.X, pady=5)
        
        result = {"action": None, "comment": None}
        
        def submit():
            action = action_var.get()
            if not action:
                messagebox.showwarning("No Action Selected", "Please select an action (Like, Comment, or Skip).")
                return
            result["action"] = action
            if result["action"] == "comment":
                result["comment"] = comment_text.get("1.0", tk.END).strip()
            dialog.destroy()
        
        def cancel():
            result["action"] = "skip"
            result["comment"] = None
            dialog.destroy()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="Submit", command=submit).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=5)
        
        dialog.transient(self.app.root)
        dialog.grab_set()
        self.app.root.wait_window(dialog)
        
        if result["action"] is None:
            result["action"] = "skip"
            result["comment"] = None
        
        return result["action"], result["comment"]

    def start_feed_interaction(self):
        if not self.check_login_status():
            return

        def get_action_callback(summary, post_index, author_name):
            self.feed_log_message(f"Opening dialog for post {post_index}", level="debug")
            self.action_queue.queue.clear()
            def run_dialog():
                action, comment = self.get_action_input(summary, post_index, author_name)
                self.feed_log_message(f"Dialog closed for post {post_index}, action: {action}", level="debug")
                self.action_queue.put((action, comment))
            
            self.app.root.after(0, run_dialog)
            action, comment = self.action_queue.get()
            return action, comment

        def feed_process():
            try:
                max_posts = self.max_posts_var.get()
                self.feed_log_message("Starting feed interaction...", clear=True, level="user")
                self.app.status_var.set("Starting feed interaction...")

                def log_callback(message, level="info"):
                    self.feed_log_message(message, level=level)

                engage_feed(self.app.driver, max_posts, get_action_callback, log_callback)
                self.feed_log_message("✅ Feed interaction completed", level="user")
                self.app.root.after(0, lambda: messagebox.showinfo("Success", "Feed interaction completed"))
                self.app.status_var.set("Feed interaction completed")

            except Exception as e:
                error_message = str(e)
                self.feed_log_message(f"❌ Error: {error_message}", level="user")
                self.app.status_var.set("Feed interaction failed")
                self.app.root.after(0, lambda msg=error_message: messagebox.showerror("Error", f"An error occurred: {msg}"))

        threading.Thread(target=feed_process, daemon=True).start()