#!/usr/bin/env python
"""
Test script to verify GUI logging functionality for LinkedIn post formatting
This version uses mock AI functions so it doesn't require the Gemini API
"""
import tkinter as tk
from tkinter import ttk
import datetime
import threading
import time

# Mock AI functions (no Gemini API required)
def mock_enhance_caption(caption):
    """Mock function that simulates the AI caption enhancement"""
    # This is a simplified version of what the real model would do
    
    # Simulate API delay
    time.sleep(1)
    
    # Create a structured post based on the template
    lines = []
    
    # HOOK
    lines.append("🚀 Just launched a powerful LinkedIn automation tool that's changing how professionals manage their online presence!")
    lines.append("")
    
    # CONTEXT
    lines.append("This project leverages Selenium for browser automation and provides seamless functionality for:")
    lines.append("✅ Creating engaging posts with smart hashtags")
    lines.append("✅ Sending personalized connection requests")
    lines.append("✅ Managing messaging at scale")
    lines.append("")
    
    # CHALLENGE
    lines.append("Building this wasn't easy - overcoming LinkedIn's dynamic UI and ensuring reliable automation required creative problem-solving and persistence.")
    lines.append("")
    
    # WHY IT MATTERS
    lines.append("For busy professionals, this tool saves countless hours of manual work while maintaining that authentic human touch that's crucial for meaningful networking.")
    lines.append("")
    
    # CALL TO ACTION
    lines.append("Have you experimented with automation for your LinkedIn activities? Share your experiences below or reach out if you'd like to learn more!")
    lines.append("")
    
    # Add the original text as a reference
    lines.append("#LinkedInAutomation #PythonDevelopment #ProductivityTools")
    
    return "\n".join(lines)

def mock_suggest_hashtags(topic):
    """Mock function that simulates hashtag suggestion"""
    # Simulate API delay
    time.sleep(0.5)
    
    # Return fixed hashtags for the demo
    return ["#LinkedInAutomation", "#PythonDevelopment", "#ProductivityTools", "#SeleniumAutomation", "#TechInnovation"]

class TestLoggingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Post Format Test (Mock AI)")
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
        
        # Result frame with accept/reject buttons
        self.result_frame = ttk.LabelFrame(main_frame, text="Enhanced Post")
        self.result_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Result text
        self.result_text = tk.Text(self.result_frame, height=15, width=80, wrap=tk.WORD)
        self.result_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Accept/Reject frame
        self.accept_frame = ttk.Frame(self.result_frame)
        self.accept_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Accept/Reject buttons
        ttk.Label(self.accept_frame, text="Use this enhanced caption?").pack(side=tk.LEFT, padx=5)
        accept_button = ttk.Button(self.accept_frame, text="Yes", command=lambda: self.respond_to_enhancement(True))
        accept_button.pack(side=tk.LEFT, padx=5)
        reject_button = ttk.Button(self.accept_frame, text="No", command=lambda: self.respond_to_enhancement(False))
        reject_button.pack(side=tk.LEFT, padx=5)
        
        # Initially hide accept/reject frame
        self.accept_frame.pack_forget()
        
    def respond_to_enhancement(self, accepted):
        """Handle user response to enhanced caption"""
        if accepted:
            self.log_message("✅ Enhanced caption accepted")
        else:
            self.log_message("❌ Enhanced caption rejected")
            self.log_message("Using original caption instead.")
            # Restore original caption
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, self.post_text.get(1.0, tk.END).strip())
            
        # Hide the acceptance frame
        self.accept_frame.pack_forget()
        
    def log_message(self, message, clear=False):
        """Add a message to the log text widget"""
        # Enable editing
        self.log_text.config(state=tk.NORMAL)
        
        if clear:
            self.log_text.delete(1.0, tk.END)
            
        # Add the message with a timestamp
        if message:
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
        """Process the post with LinkedIn formatting using mock functions"""
        
        def run_formatting():
            # Get the post text
            post_text = self.post_text.get("1.0", tk.END).strip()
            if not post_text:
                self.log_message("Please enter some text for your post", clear=True)
                return
                
            self.log_message("Starting LinkedIn post formatting...", clear=True)
            
            try:
                # Enhance caption using mock function
                self.log_message("Enhancing caption with AI...")
                enhanced = mock_enhance_caption(post_text)
                
                # Show the result
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, enhanced)
                
                self.log_message("\n🤖 AI-Enhanced Caption:")
                self.log_message(enhanced)
                
                # Show accept/reject buttons
                self.accept_frame.pack(fill=tk.X, padx=5, pady=5)
                
                # Generate hashtags using mock function
                self.log_message("\nGenerating smart hashtags...")
                hashtags = mock_suggest_hashtags(post_text)
                
                self.log_message(f"Suggested hashtags: {' '.join(hashtags)}")
                
                self.log_message("\n✅ Post formatting completed successfully!")
                
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