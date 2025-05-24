#!/usr/bin/env python
"""
Test script to verify GUI logging functionality for LinkedIn post formatting
"""
import tkinter as tk
from tkinter import ttk

class TestLoggingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Post Format Test")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create input area
        input_frame = ttk.LabelFrame(main_frame, text="Post Input")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Text input
        ttk.Label(input_frame, text="Enter your LinkedIn post:").pack(anchor=tk.W, pady=5)
        self.post_text = tk.Text(input_frame, height=5, width=80, wrap=tk.WORD)
        self.post_text.pack(fill=tk.X, padx=5, pady=5)
        self.post_text.insert(tk.END, "I'm excited to share that I just completed a LinkedIn automation project! It uses Selenium for browser automation and has features for posting, messaging, and connection requests.")
        
        # Button to process
        process_button = ttk.Button(input_frame, text="Format Post", command=self.process_post)
        process_button.pack(pady=10)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Format Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log text with scrollbar
        self.log_text = tk.Text(log_frame, height=20, width=80, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Result frame
        self.result_frame = ttk.LabelFrame(main_frame, text="Enhanced Post")
        self.result_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Result text
        self.result_text = tk.Text(self.result_frame, height=15, width=80, wrap=tk.WORD)
        self.result_text.pack(fill=tk.X, padx=5, pady=5)
        
    def log_message(self, message, clear=False):
        """Add a message to the log text widget"""
        # Enable editing
        self.log_text.config(state=tk.NORMAL)
        
        if clear:
            self.log_text.delete(1.0, tk.END)
            
        # Add the message with a timestamp
        if message:
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            self.log_text.insert(tk.END, formatted_message)
            
        # Auto-scroll to the end
        self.log_text.see(tk.END)
        
        # Disable editing again
        self.log_text.config(state=tk.DISABLED)
        
        # Update the GUI immediately
        self.root.update_idletasks()
    
    def process_post(self):
        """Process the post with LinkedIn formatting"""
        import threading
        
        def run_formatting():
            # Get the post text
            post_text = self.post_text.get("1.0", tk.END).strip()
            if not post_text:
                self.log_message("Please enter some text for your post", clear=True)
                return
                
            self.log_message("Starting LinkedIn post formatting...", clear=True)
            
            try:
                # Import AI functions
                import sys
                import os
                project_root = os.path.dirname(os.path.abspath(__file__))
                sys.path.insert(0, project_root)
                
                try:
                    from ai.ai_generator import enhance_caption, suggest_hashtags
                    
                    # Enhance the caption
                    self.log_message("Enhancing caption with AI...")
                    enhanced = enhance_caption(post_text)
                    
                    # Show the result
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, enhanced)
                    
                    self.log_message("\n🤖 AI-Enhanced Caption:")
                    self.log_message(enhanced)
                    
                    # Generate hashtags
                    self.log_message("\nGenerating smart hashtags...")
                    hashtags = suggest_hashtags(post_text)
                    
                    self.log_message(f"Suggested hashtags: {' '.join(hashtags)}")
                    
                    self.log_message("\n✅ Post formatting completed successfully!")
                    
                except ImportError as e:
                    self.log_message(f"❌ Could not import AI functions: {e}")
                    self.log_message("Make sure you have the required packages installed.")
                    
            except Exception as e:
                self.log_message(f"❌ Error during post formatting: {e}")
        
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=run_formatting, daemon=True).start()

def main():
    root = tk.Tk()
    app = TestLoggingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 