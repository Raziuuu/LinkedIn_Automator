import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
import time
from selenium.webdriver.common.by import By
from PIL import Image, ImageTk

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from automation.linkedin_automation import create_driver, load_credentials, login_linkedin
from automation.connection_requester import process_connections
from automation.post_creator import create_linkedin_post
from automation.message_bot import start_bulk_messaging, open_messaging_page, send_message
from automation.feed_scroller import engage_feed
from gui.utils import create_tooltip, long_operation, create_scrollable_frame

class LinkedInAutomatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Automator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set application icon
        try:
            logo_path = "assets/logo.png"
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
        
        # Create tabs
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
        
        # Set up each tab
        self.setup_login_tab()
        self.setup_connection_tab()
        self.setup_post_tab()
        self.setup_message_tab()
        self.setup_feed_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Not logged in")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Connection counters
        self.connections_sent = 0
        self.connections_skipped = 0
        self.connections_saved = 0
    
    def setup_login_tab(self):
        frame = ttk.LabelFrame(self.login_tab, text="LinkedIn Login")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Login status indicator
        self.login_status_var = tk.StringVar()
        self.login_status_var.set("Not logged in")
        status_label = ttk.Label(frame, textvariable=self.login_status_var, font=("Arial", 12))
        status_label.pack(pady=10)
        
        # Login button
        login_button = ttk.Button(frame, text="Login to LinkedIn", command=self.login_to_linkedin)
        login_button.pack(pady=10)
        create_tooltip(login_button, "Login to your LinkedIn account using saved credentials")
        
        # Logout button
        logout_button = ttk.Button(frame, text="Logout", command=self.logout_from_linkedin)
        logout_button.pack(pady=10)
        create_tooltip(logout_button, "Close browser and log out from LinkedIn")
    
    def setup_connection_tab(self):
        # Use scrollable frame for the connection tab
        outer_frame, frame = create_scrollable_frame(self.connection_tab)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection configuration
        config_frame = ttk.LabelFrame(frame, text="Connection Request Settings")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Number of requests
        ttk.Label(config_frame, text="Max Connection Requests:").pack(anchor=tk.W, pady=5)
        self.max_requests_var = tk.IntVar(value=5)
        max_requests_spinbox = ttk.Spinbox(config_frame, from_=1, to=20, textvariable=self.max_requests_var)
        max_requests_spinbox.pack(fill=tk.X, pady=5)
        create_tooltip(max_requests_spinbox, "Maximum number of connection requests to send")
        
        # Start connection requests button
        start_button = ttk.Button(config_frame, text="Start Connection Requests", 
                                command=self.send_connection_requests)
        start_button.pack(pady=10)
        create_tooltip(start_button, "Start processing connection requests")
        
        # Connections action frame
        self.connection_actions_frame = ttk.LabelFrame(frame, text="Connection Profile")
        self.connection_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Profile info frame
        profile_info_frame = ttk.Frame(self.connection_actions_frame)
        profile_info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add a border around the profile info
        profile_box = ttk.Frame(profile_info_frame, relief=tk.GROOVE, borderwidth=2)
        profile_box.pack(fill=tk.X, padx=5, pady=5)
        
        # Current connection info
        self.current_connection_var = tk.StringVar(value="No connections loaded")
        current_connection_label = ttk.Label(profile_box, 
                                          textvariable=self.current_connection_var,
                                          font=("Arial", 10, "bold"),
                                          wraplength=500,
                                          justify=tk.LEFT,
                                          padding=(10, 10))
        current_connection_label.pack(pady=10, padx=10, fill=tk.X)
        
        # Decision input
        decision_frame = ttk.Frame(self.connection_actions_frame)
        decision_frame.pack(fill=tk.X, pady=5)
        ttk.Label(decision_frame, text="Send request? [y/n/l]:").pack(side=tk.LEFT)
        self.decision_entry = ttk.Entry(decision_frame, width=10)
        self.decision_entry.pack(side=tk.LEFT, padx=5)
        self.decision_button = ttk.Button(decision_frame, text="Submit", command=self.submit_decision)
        self.decision_button.pack(side=tk.LEFT)
        create_tooltip(self.decision_entry, "Enter y (send), n (skip), or l (save for later)")
        
        # Button frame for actions
        button_frame = ttk.Frame(self.connection_actions_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Create a style for the green button
        self.root.style = ttk.Style() 
        self.root.style.configure('Green.TButton', background='green')
        
        # Send button
        send_button = ttk.Button(button_frame, text="Send Request ✓", 
                               style='Green.TButton',
                               command=lambda: self.process_connection_action("y"))
        send_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        create_tooltip(send_button, "Send connection request to this person")
        
        # Skip button
        skip_button = ttk.Button(button_frame, text="Skip ✗", 
                               command=lambda: self.process_connection_action("n"))
        skip_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        create_tooltip(skip_button, "Skip this connection suggestion")
        
        # Save for later button
        save_button = ttk.Button(button_frame, text="Save for Later 📌", 
                               command=lambda: self.process_connection_action("l"))
        save_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        create_tooltip(save_button, "Save this profile for later review")
        
        # Initially hide the actions frame
        self.connection_actions_frame.pack_forget()
        
        # Add log display area
        log_frame = ttk.LabelFrame(frame, text="Connection Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log filter controls
        log_filter_frame = ttk.Frame(log_frame)
        log_filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(log_filter_frame, text="Show log level:").pack(side=tk.LEFT, padx=5)
        self.connection_log_level_var = tk.StringVar(value="user")
        connection_log_level_combo = ttk.Combobox(log_filter_frame, textvariable=self.connection_log_level_var, width=15)
        connection_log_level_combo['values'] = ("user", "info", "debug")
        connection_log_level_combo.pack(side=tk.LEFT, padx=5)
        create_tooltip(connection_log_level_combo, "Filter log messages by importance")
        
        connection_log_level_combo.bind('<<ComboboxSelected>>', self.update_connection_log_display)
        
        # Log text widget with scrollbar
        self.connection_log_text = tk.Text(log_frame, height=15, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.connection_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        connection_log_scrollbar = ttk.Scrollbar(log_frame, command=self.connection_log_text.yview)
        connection_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.connection_log_text.config(yscrollcommand=connection_log_scrollbar.set)
        
        # Store connection log messages
        self.connection_log_messages = []
        
        # Connection summary frame
        summary_frame = ttk.LabelFrame(frame, text="Connection Summary")
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Summary stats
        summary_stats_frame = ttk.Frame(summary_frame)
        summary_stats_frame.pack(fill=tk.X, pady=5)
        
        # Total processed
        ttk.Label(summary_stats_frame, text="Total Processed:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_processed_var = tk.StringVar(value="0")
        ttk.Label(summary_stats_frame, textvariable=self.total_processed_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Sent
        ttk.Label(summary_stats_frame, text="Sent:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_sent_var = tk.StringVar(value="0")
        ttk.Label(summary_stats_frame, textvariable=self.total_sent_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Skipped
        ttk.Label(summary_stats_frame, text="Skipped:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_skipped_var = tk.StringVar(value="0")
        ttk.Label(summary_stats_frame, textvariable=self.total_skipped_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Saved for later
        ttk.Label(summary_stats_frame, text="Saved for Later:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.total_saved_var = tk.StringVar(value="0")
        ttk.Label(summary_stats_frame, textvariable=self.total_saved_var).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        # State variables for decision input
        self.decision_var = tk.StringVar()
        self.running = False
    
    def setup_post_tab(self):
        # Use scrollable frame for the post tab
        outer_frame, frame = create_scrollable_frame(self.post_tab)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Post creation section
        post_frame = ttk.LabelFrame(frame, text="Create LinkedIn Post")
        post_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Caption
        ttk.Label(post_frame, text="Post Caption:").pack(anchor=tk.W, pady=5)
        self.caption_text = tk.Text(post_frame, height=5, width=50)
        self.caption_text.pack(fill=tk.X, pady=5)
        create_tooltip(self.caption_text, "Enter the text for your LinkedIn post")
        
        # Image options
        self.use_image_var = tk.BooleanVar(value=False)
        use_image_check = ttk.Checkbutton(post_frame, text="Include Image", variable=self.use_image_var, command=self.toggle_image_selection)
        use_image_check.pack(anchor=tk.W, pady=5)
        create_tooltip(use_image_check, "Check to include an image with your post")
        
        # Image selection frame
        self.image_frame = ttk.Frame(post_frame)
        self.image_frame.pack(fill=tk.X, pady=5)
        self.image_frame.pack_forget()  # Hidden by default
        
        # Image path
        self.image_path_var = tk.StringVar()
        ttk.Label(self.image_frame, text="Image Path:").pack(side=tk.LEFT, padx=5)
        image_path_entry = ttk.Entry(self.image_frame, textvariable=self.image_path_var, width=40)
        image_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        browse_button = ttk.Button(self.image_frame, text="Browse", command=self.browse_image)
        browse_button.pack(side=tk.LEFT, padx=5)
        create_tooltip(browse_button, "Select an image file from your computer")
        
        # Smart hashtags
        self.smart_hashtags_var = tk.BooleanVar(value=True)
        smart_hashtags_check = ttk.Checkbutton(post_frame, text="Use Smart Hashtags", variable=self.smart_hashtags_var)
        smart_hashtags_check.pack(anchor=tk.W, pady=5)
        create_tooltip(smart_hashtags_check, "Automatically generate relevant hashtags for your post")
        
        # Add log display area
        log_frame = ttk.LabelFrame(frame, text="AI Enhancement Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log filter controls
        log_filter_frame = ttk.Frame(log_frame)
        log_filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(log_filter_frame, text="Show log level:").pack(side=tk.LEFT, padx=5)
        self.log_level_var = tk.StringVar(value="user")
        log_level_combo = ttk.Combobox(log_filter_frame, textvariable=self.log_level_var, width=15)
        log_level_combo['values'] = ("user", "info", "debug")
        log_level_combo.pack(side=tk.LEFT, padx=5)
        create_tooltip(log_level_combo, "Filter log messages by importance")
        
        log_level_combo.bind('<<ComboboxSelected>>', self.update_log_display)
        
        # Log text widget with scrollbar
        self.log_text = tk.Text(log_frame, height=15, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Store log messages
        self.log_messages = []
        
        # Enhanced caption acceptance frame
        self.enhanced_caption_frame = ttk.Frame(frame, relief=tk.RAISED, borderwidth=3)
        self.enhanced_caption_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add a clear label to the frame
        ttk.Label(self.enhanced_caption_frame, text="AI CAPTION REVIEW", font=("Arial", 12, "bold")).pack(side=tk.TOP, padx=5, pady=5)
        
        # Enhanced caption acceptance buttons
        response_frame = ttk.Frame(self.enhanced_caption_frame)
        response_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Label(response_frame, text="Use this enhanced caption?").pack(side=tk.LEFT, padx=5)
        accept_button = ttk.Button(response_frame, text="Yes", command=lambda: self.respond_to_enhancement(True))
        accept_button.pack(side=tk.LEFT, padx=5)
        reject_button = ttk.Button(response_frame, text="No", command=lambda: self.respond_to_enhancement(False))
        reject_button.pack(side=tk.LEFT, padx=5)
        
        # Initially hide the acceptance frame
        self.enhanced_caption_frame.pack_forget()
        
        # Post button
        post_button = ttk.Button(post_frame, text="Create Post", command=self.create_post)
        post_button.pack(pady=10)
        create_tooltip(post_button, "Create and publish your LinkedIn post")
    
    def setup_message_tab(self):
        # Use scrollable frame for the message tab
        outer_frame, frame = create_scrollable_frame(self.message_tab)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Message configuration section
        config_frame = ttk.LabelFrame(frame, text="Message Configuration")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Messaging mode selection
        ttk.Label(config_frame, text="Messaging Mode:").pack(anchor=tk.W, pady=5)
        self.message_mode_var = tk.StringVar(value="specific")
        mode_frame = ttk.Frame(config_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(mode_frame, text="Broadcast to recent contacts", 
                       variable=self.message_mode_var, value="broadcast").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Select specific contacts", 
                       variable=self.message_mode_var, value="specific").pack(side=tk.LEFT, padx=10)
        
        # Message tone selection
        ttk.Label(config_frame, text="Message Tone:").pack(anchor=tk.W, pady=5)
        self.message_tone_var = tk.StringVar(value="professional")
        tone_frame = ttk.Frame(config_frame)
        tone_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(tone_frame, text="Professional", 
                       variable=self.message_tone_var, value="professional").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(tone_frame, text="Friendly", 
                       variable=self.message_tone_var, value="friendly").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(tone_frame, text="Casual", 
                       variable=self.message_tone_var, value="casual").pack(side=tk.LEFT, padx=10)
        
        # Contact list section
        contacts_frame = ttk.LabelFrame(frame, text="Contact Selection")
        contacts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Button to load contacts
        load_contacts_button = ttk.Button(contacts_frame, text="Load Recent Contacts", 
                                         command=self.load_recent_contacts)
        load_contacts_button.pack(pady=10)
        
        # Contacts listbox with selection
        self.contacts_listbox_frame = ttk.Frame(contacts_frame)
        self.contacts_listbox_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(self.contacts_listbox_frame, text="Select contacts to message:").pack(anchor=tk.W)
        
        listbox_frame = ttk.Frame(self.contacts_listbox_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.contacts_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, height=10)
        self.contacts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        contacts_scrollbar = ttk.Scrollbar(listbox_frame, command=self.contacts_listbox.yview)
        contacts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.contacts_listbox.config(yscrollcommand=contacts_scrollbar.set)
        
        # Initially hide the contacts listbox
        self.contacts_listbox_frame.pack_forget()
        
        # Store contacts data
        self.contacts_data = []
        
        # Topic/Context input section
        self.topic_frame = ttk.LabelFrame(frame, text="Message Content")
        self.topic_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add instructions
        instruction_text = "Enter what you want to talk about. AI will create a personalized message based on this input."
        instruction_label = ttk.Label(self.topic_frame, text=instruction_text, wraplength=600)
        instruction_label.pack(anchor=tk.W, pady=5)
        
        ttk.Label(self.topic_frame, text="Your message topic or context:").pack(anchor=tk.W, pady=5)
        self.topic_text = tk.Text(self.topic_frame, height=4, width=50)
        self.topic_text.pack(fill=tk.X, pady=5)
        create_tooltip(self.topic_text, "Describe what you want to talk about. AI will create a message based on this.")
        
        # Example label
        example_text = "Example: I'd like to discuss potential collaboration on AI projects in the healthcare sector."
        example_label = ttk.Label(self.topic_frame, text=example_text, font=("Arial", 9, "italic"), foreground="gray")
        example_label.pack(anchor=tk.W, pady=5)
        
        # Resume options
        self.use_resume_var = tk.BooleanVar(value=False)
        use_resume_check = ttk.Checkbutton(self.topic_frame, text="Attach Resume", variable=self.use_resume_var, command=self.toggle_resume_selection)
        use_resume_check.pack(anchor=tk.W, pady=5)
        create_tooltip(use_resume_check, "Check to attach a resume with your message")
        
        # Resume selection frame
        self.resume_frame = ttk.Frame(self.topic_frame)
        self.resume_frame.pack(fill=tk.X, pady=5)
        self.resume_frame.pack_forget()  # Hidden by default
        
        # Resume path
        self.resume_path_var = tk.StringVar()
        ttk.Label(self.resume_frame, text="Resume Path:").pack(side=tk.LEFT, padx=5)
        resume_path_entry = ttk.Entry(self.resume_frame, textvariable=self.resume_path_var, width=40)
        resume_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        browse_button = ttk.Button(self.resume_frame, text="Browse", command=self.browse_resume)
        browse_button.pack(side=tk.LEFT, padx=5)
        create_tooltip(browse_button, "Select a resume file (PDF) from your computer")
        
        # Initially hide the topic frame
        self.topic_frame.pack_forget()
        
        # Message preview section
        message_preview_frame = ttk.LabelFrame(frame, text="AI Generated Message")
        message_preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Preview button
        preview_button = ttk.Button(message_preview_frame, text="Generate Message with AI", 
                                   command=self.generate_message_preview)
        preview_button.pack(pady=10)
        create_tooltip(preview_button, "Generate a personalized message based on your topic and selected tone")
        
        # Message preview text
        self.message_preview_text = tk.Text(message_preview_frame, height=10, width=50, state=tk.DISABLED)
        self.message_preview_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Edit button
        edit_button = ttk.Button(message_preview_frame, text="Edit Message", 
                                command=self.edit_message_template)
        edit_button.pack(pady=10)
        create_tooltip(edit_button, "Customize the AI-generated message")
        
        # Send messages section
        send_frame = ttk.Frame(frame)
        send_frame.pack(fill=tk.X, padx=10, pady=10)
        
        send_button = ttk.Button(send_frame, text="Send Messages", 
                                command=self.start_messaging)
        send_button.pack(side=tk.LEFT, padx=5)
        create_tooltip(send_button, "Start sending messages to selected contacts")
        
        # Messaging log section
        log_frame = ttk.LabelFrame(frame, text="Messaging Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log level filter
        log_filter_frame = ttk.Frame(log_frame)
        log_filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(log_filter_frame, text="Show log level:").pack(side=tk.LEFT, padx=5)
        self.messaging_log_level_var = tk.StringVar(value="user")
        messaging_log_level_combo = ttk.Combobox(log_filter_frame, textvariable=self.messaging_log_level_var, width=15)
        messaging_log_level_combo['values'] = ("user", "info", "debug")
        messaging_log_level_combo.pack(side=tk.LEFT, padx=5)
        create_tooltip(messaging_log_level_combo, "Filter log messages by importance")
        
        messaging_log_level_combo.bind('<<ComboboxSelected>>', self.update_messaging_log_display)
        
        # Messaging log text
        self.messaging_log_text = tk.Text(log_frame, height=10, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.messaging_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        messaging_log_scrollbar = ttk.Scrollbar(log_frame, command=self.messaging_log_text.yview)
        messaging_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.messaging_log_text.config(yscrollcommand=messaging_log_scrollbar.set)
        
        # Initialize message log data
        self.messaging_log_messages = []
    
    def setup_feed_tab(self):
        # Use scrollable frame for the feed tab
        outer_frame, frame = create_scrollable_frame(self.feed_tab)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Feed interaction section
        config_frame = ttk.LabelFrame(frame, text="Feed Interaction")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Information label
        info_text = "Interact with LinkedIn posts by liking, commenting, or skipping. AI will summarize each post."
        info_label = ttk.Label(config_frame, text=info_text, wraplength=600)
        info_label.pack(pady=10)
        
        # Number of posts to interact with
        ttk.Label(config_frame, text="Max Posts to Interact With:").pack(anchor=tk.W, pady=5)
        self.max_posts_var = tk.IntVar(value=5)
        max_posts_spinbox = ttk.Spinbox(config_frame, from_=1, to=20, textvariable=self.max_posts_var)
        max_posts_spinbox.pack(fill=tk.X, pady=5)
        create_tooltip(max_posts_spinbox, "Maximum number of posts to scroll through and interact with")
        
        # Start feed interaction button
        feed_button = ttk.Button(config_frame, text="Start Feed Interaction", command=self.start_feed_interaction)
        feed_button.pack(pady=10)
        create_tooltip(feed_button, "Start scrolling through your feed and interacting with posts")
        
        # Add log display area
        log_frame = ttk.LabelFrame(frame, text="Feed Interaction Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log filter controls
        log_filter_frame = ttk.Frame(log_frame)
        log_filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(log_filter_frame, text="Show log level:").pack(side=tk.LEFT, padx=5)
        self.feed_log_level_var = tk.StringVar(value="user")
        feed_log_level_combo = ttk.Combobox(log_filter_frame, textvariable=self.feed_log_level_var, width=15)
        feed_log_level_combo['values'] = ("user", "info", "debug")
        feed_log_level_combo.pack(side=tk.LEFT, padx=5)
        create_tooltip(feed_log_level_combo, "Filter log messages by importance")
        
        feed_log_level_combo.bind('<<ComboboxSelected>>', self.update_feed_log_display)
        
        # Log text widget with scrollbar
        self.feed_log_text = tk.Text(log_frame, height=15, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.feed_log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        feed_log_scrollbar = ttk.Scrollbar(log_frame, command=self.feed_log_text.yview)
        feed_log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.feed_log_text.config(yscrollcommand=feed_log_scrollbar.set)
        
        # Store feed log messages
        self.feed_log_messages = []
    
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
        
        self.feed_log_text.config(state=tk.NORMAL)
        
        if clear:
            self.feed_log_text.delete(1.0, tk.END)
            
        if message and show_message:
            formatted_message = f"[{timestamp}] {prefix}{message}\n"
            self.feed_log_text.insert(tk.END, formatted_message)
            
        self.feed_log_text.see(tk.END)
        self.feed_log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_feed_log_display(self, event=None):
        selected_level = self.feed_log_level_var.get()
        
        self.feed_log_text.config(state=tk.NORMAL)
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
        
        self.feed_log_text.config(state=tk.DISABLED)
        self.feed_log_text.see(tk.END)
    
    def output_callback(self, message, level="info"):
        self.connection_log_message(message, level=level)
        if level == "user" and "👤" in message:
            profile_lines = message.split("\n")
            profile_text = "\n".join(line for line in profile_lines if any(icon in line for icon in ["👤", "💼", "📍", "🎓", "🏢"]))
            self.current_connection_var.set(profile_text)
    
    def decision_callback(self):
        self.decision_entry.delete(0, tk.END)
        self.decision_var.set("")
        self.decision_entry.focus_set()
        self.root.wait_variable(self.decision_var)
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
    
    def update_connection_counters(self):
        total = self.connections_sent + self.connections_skipped + self.connections_saved
        self.total_processed_var.set(str(total))
        self.total_sent_var.set(str(self.connections_sent))
        self.total_skipped_var.set(str(self.connections_skipped))
        self.total_saved_var.set(str(self.connections_saved))
        
        if total > 0:
            self.status_var.set(f"Processed {total} connections ({self.connections_sent} sent, {self.connections_skipped} skipped, {self.connections_saved} saved)")
        else:
            self.status_var.set("No connections processed")
    
    def load_recent_contacts(self):
        if not self.check_login_status():
            return
            
        self.messaging_log_message("Loading recent contacts...", clear=True, level="user")
        
        def load_contacts_process():
            try:
                from automation.message_bot import open_messaging_page, get_recent_conversations
                
                self.messaging_log_message("Opening LinkedIn messaging page...", level="info")
                open_messaging_page(self.driver)
                
                self.messaging_log_message("Finding recent conversations...", level="info")
                contacts = get_recent_conversations(self.driver)
                
                self.contacts_data = contacts
                self.root.after(0, self.update_contacts_listbox, contacts)
                
                self.messaging_log_message(f"Found {len(contacts)} recent contacts", level="user")
            except Exception as e:
                self.messaging_log_message(f"Error loading contacts: {e}", level="user")
                
        threading.Thread(target=load_contacts_process, daemon=True).start()
        
    def update_contacts_listbox(self, contacts):
        self.contacts_data = contacts
        
        self.contacts_listbox.delete(0, tk.END)
        
        for name, _ in contacts:
            self.contacts_listbox.insert(tk.END, name)
            
        self.contacts_listbox_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.topic_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.messaging_log_message("✅ Contacts loaded successfully.", level="user")
        self.messaging_log_message("👉 Select contacts and enter a message topic, then click Generate Message Preview", level="user")
        
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
            5. Acknowledge the recipient's role or company (e.g., 'your work at [company]') without needing specific details
            6. Include a clear call to action for a referral or conversation
            7. Mention that a resume is attached
            8. Make it sound natural, concise, and professional
            9. DO NOT use greetings like 'Hi {recipient_name}, I came across your profile'
            10. Vary phrasing slightly based on tone (professional: formal, friendly: warm, casual: relaxed)
            
            Example for topic 'Java Developer internship at Cognizant', professional tone:
            {recipient_name}, I'm excited about the Java Developer internship at Cognizant and admire the innovative work being done there. Given your expertise, could you kindly consider referring me or sharing any insights? I've attached my resume and would love to chat further!
            
            Return only the message text.
            """
            
            message = generate_text(prompt)
            
            if message:
                message = message.strip('"\'')
                self.message_preview_text.config(state=tk.NORMAL)
                self.message_preview_text.delete("1.0", tk.END)
                self.message_preview_text.insert(tk.END, message)
                self.message_preview_text.config(state=tk.NORMAL)
                
                self.messaging_log_message("✅ Message preview generated with AI", level="user")
            else:
                self.message_preview_text.config(state=tk.NORMAL)
                self.message_preview_text.delete("1.0", tk.END)
                simple_message = f"{recipient_name}, I'm interested in {topic}. Could we discuss this? I've attached my resume."
                self.message_preview_text.insert(tk.END, simple_message)
                self.message_preview_text.config(state=tk.DISABLED)
                
                self.messaging_log_message("⚠️ Could not enhance message with AI, using basic message", level="user")
        
        except Exception as e:
            self.messaging_log_message(f"❌ Error generating message preview: {str(e)}", level="user")
            self.message_preview_text.config(state=tk.NORMAL)
            self.message_preview_text.delete("1.0", tk.END)
            simple_message = f"{recipient_name}, I'm interested in {topic}. Could we discuss this? I've attached my resume."
            self.message_preview_text.insert(tk.END, simple_message)
            self.message_preview_text.config(state=tk.DISABLED)
    
    def edit_message_template(self):
        self.message_preview_text.config(state=tk.NORMAL)
        self.messaging_log_message("You can now edit the message template", level="info")
    
    def toggle_resume_selection(self):
        if self.use_resume_var.get():
            self.resume_frame.pack(fill=tk.X, pady=5)
        else:
            self.resume_frame.pack_forget()
    
    def browse_resume(self):
        file_path = filedialog.askopenfilename(
            title="Select Resume",
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
        
        self.messaging_log_text.config(state=tk.NORMAL)
        
        if clear:
            self.messaging_log_text.delete(1.0, tk.END)
            
        if message and show_message:
            formatted_message = f"[{timestamp}] {prefix}{message}\n"
            self.messaging_log_text.insert(tk.END, formatted_message)
            
        self.messaging_log_text.see(tk.END)
        self.messaging_log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_messaging_log_display(self, event=None):
        selected_level = self.messaging_log_level_var.get()
        
        self.messaging_log_text.config(state=tk.NORMAL)
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
        
        self.messaging_log_text.config(state=tk.DISABLED)
        self.messaging_log_text.see(tk.END)
    
    def toggle_image_selection(self):
        if self.use_image_var.get():
            self.image_frame.pack(fill=tk.X, pady=5)
        else:
            self.image_frame.pack_forget()
    
    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.image_path_var.set(file_path)
    
    def login_to_linkedin(self):
        def login_process():
            try:
                self.status_var.set("Loading credentials...")
                self.root.update_idletasks()
                
                creds = load_credentials()
                
                self.status_var.set("Creating browser driver...")
                self.root.update_idletasks()
                
                self.driver = create_driver()
                
                self.status_var.set("Logging in to LinkedIn...")
                self.root.update_idletasks()
                
                success = login_linkedin(self.driver, creds["username"], creds["password"])
                
                if success:
                    self.is_logged_in = True
                    self.status_var.set("Logged in successfully")
                    self.login_status_var.set("Logged in as: " + creds["username"])
                else:
                    self.status_var.set("Login failed")
                    self.login_status_var.set("Login failed")
                    if self.driver:
                        self.driver.quit()
                        self.driver = None
            except Exception as e:
                self.status_var.set(f"Error: {e}")
                self.login_status_var.set("Login error")
                if self.driver:
                    self.driver.quit()
                    self.driver = None
        
        threading.Thread(target=login_process, daemon=True).start()
    
    def logout_from_linkedin(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False
            self.status_var.set("Logged out")
            self.login_status_var.set("Not logged in")
    
    def send_connection_requests(self):
        if not self.check_login_status():
            return
        
        if self.running:
            messagebox.showwarning("Warning", "Connection request process is already running.")
            return
            
        max_requests = self.max_requests_var.get()
        
        self.running = True
        self.connections_sent = 0
        self.connections_skipped = 0
        self.connections_saved = 0
        self.update_connection_counters()
        
        self.connection_actions_frame.pack(fill=tk.X, padx=10, pady=10)
        self.notebook.select(self.connection_tab)
        
        def connection_process():
            try:
                self.status_var.set("Starting connection requests...")
                self.connection_log_message("Starting connection request process...", clear=True, level="user")
                
                def log_callback(message, level="info"):
                    self.connection_log_message(message, level=level)
                
                initial_processed = self.connections_sent + self.connections_skipped + self.connections_saved
                
                process_connections(
                    self.driver,
                    max_requests=max_requests,
                    output_callback=log_callback,
                    decision_callback=self.decision_callback,
                    counter_callback=self.update_connection_counters
                )
                
                total_processed = self.connections_sent + self.connections_skipped + self.connections_saved
                if total_processed == initial_processed:
                    self.connection_log_message("⚠️ No profiles were found to process. Check LinkedIn network page or try again later.", level="user")
                    messagebox.showwarning("Warning", "No profiles were found to process. Please check the LinkedIn 'My Network' page or try again later.")
                    self.status_var.set("No connections processed")
                else:
                    self.status_var.set(f"Processed {total_processed} connections")
                    self.connection_log_message(f"✅ Completed. Processed {total_processed} connections", level="user")
                    messagebox.showinfo("Success", f"Connection request process completed. Processed {total_processed} connections.")
                
            except Exception as e:
                self.status_var.set(f"Error in connection requests: {e}")
                self.connection_log_message(f"❌ Error: {e}", level="user")
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                self.running = False
                self.connection_actions_frame.pack_forget()
        
        threading.Thread(target=connection_process, daemon=True).start()
    
    def respond_to_enhancement(self, accepted):
        self.enhancement_accepted = accepted
        
        if accepted:
            self.log_message("✅ Enhanced caption ACCEPTED", level="user")
        else:
            self.log_message("❌ Enhanced caption REJECTED", level="user")
            
        self.enhanced_caption_frame.pack_forget()
        self.root.update()
    
    def update_log_display(self, event=None):
        selected_level = self.log_level_var.get()
        
        self.log_text.config(state=tk.NORMAL)
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
        
        self.log_text.config(state=tk.DISABLED)
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
        
        self.log_text.config(state=tk.NORMAL)
        
        if clear:
            self.log_text.delete(1.0, tk.END)
            
        if message and show_message:
            formatted_message = f"[{timestamp}] {prefix}{message}\n"
            self.log_text.insert(tk.END, formatted_message)
            
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def create_post(self):
        if not self.check_login_status():
            return
        
        def post_process():
            try:
                caption = self.caption_text.get("1.0", tk.END).strip()
                if not caption:
                    messagebox.showerror("Error", "Please enter a caption for your post")
                    self.status_var.set("Post creation canceled: No caption")
                    return
                
                image_path = None
                if self.use_image_var.get():
                    image_path = self.image_path_var.get()
                    if not image_path or not os.path.exists(image_path):
                        messagebox.showerror("Error", "Please select a valid image file")
                        self.status_var.set("Post creation canceled: Invalid image")
                        return
                
                self.status_var.set("Creating LinkedIn post...")
                self.log_message("Starting LinkedIn post creation...", clear=True, level="user")
                
                from ai.ai_generator import enhance_caption, detect_topic_and_hashtags
                
                def remove_non_bmp(text):
                    return ''.join(char for char in text if ord(char) < 0x10000)
                
                clean_caption = remove_non_bmp(caption)
                
                try:
                    self.log_message("Enhancing caption with AI...", level="user")
                    enhanced_caption = enhance_caption(clean_caption)
                    enhanced_caption = remove_non_bmp(enhanced_caption)
                    
                    self.log_message("\n🤖 AI-Enhanced Caption:", level="user")
                    self.log_message(enhanced_caption, level="user")
                    self.log_message("Using AI-enhanced caption automatically", level="info")
                except Exception as e:
                    self.log_message(f"Could not enhance caption with AI: {e}", level="user")
                    self.log_message("Continuing with original caption.", level="info")
                    enhanced_caption = clean_caption
                
                smart = self.smart_hashtags_var.get()
                
                if smart:
                    try:
                        self.log_message("Generating smart hashtags...", level="info")
                        topic, hashtags = detect_topic_and_hashtags(enhanced_caption)
                        self.log_message(f"Detected topic: {topic}", level="info")
                        self.log_message(f"Suggested hashtags: {' '.join(hashtags)}", level="user")
                    except Exception as e:
                        self.log_message(f"Smart hashtag detection failed: {e}", level="debug")
                        self.log_message("Continuing without hashtags.", level="info")
                
                self.log_message("Submitting post to LinkedIn...", level="user")
                def log_wrapper(message, level="info"):
                    self.log_message(message, level=level)
                
                success = create_linkedin_post(self.driver, enhanced_caption, image_path, smart, log_callback=log_wrapper)
                
                if success:
                    self.status_var.set("Post created successfully")
                    self.log_message("Post created successfully!", level="user")
                    self.caption_text.delete("1.0", tk.END)
                    self.image_path_var.set("")
                else:
                    self.status_var.set("Failed to create post")
                    self.log_message("Failed to create post.", level="user")
            except Exception as e:
                self.status_var.set(f"Error creating post: {e}")
                self.log_message(f"Error creating post: {e}", level="user")
        
        long_operation(
            post_process, 
            self.status_var, 
            self.root,
            "Post created successfully",
            "Error creating post"
        )
    
    def start_messaging(self):
        if not self.check_login_status():
            return
        
        if not self.contacts_data:
            messagebox.showerror("Error", "Please load contacts first")
            return
            
        selected_indices = self.contacts_listbox.curselection()
        
        if not selected_indices and self.message_mode_var.get() == "specific":
            messagebox.showerror("Error", "Please select at least one contact")
            return
        
        message = self.message_preview_text.get("1.0", tk.END).strip()
        
        if not message:
            topic = self.topic_text.get("1.0", tk.END).strip()
            if not topic:
                messagebox.showerror("Error", "Please enter a topic and generate a message preview")
                return
            self.generate_message_preview()
            message = self.message_preview_text.get("1.0", tk.END).strip()
            
        if not message:
            messagebox.showerror("Error", "Please generate a message preview first")
            return
        
        resume_path = None
        if self.use_resume_var.get():
            resume_path = self.resume_path_var.get()
            if not resume_path or not os.path.exists(resume_path):
                messagebox.showerror("Error", "Please select a valid resume file")
                self.status_var.set("Messaging canceled: Invalid resume")
                return
        
        def messaging_process():
            try:
                self.status_var.set("Starting bulk messaging...")
                self.messaging_log_message("Starting LinkedIn messaging...", clear=True, level="user")
                
                def log_callback(message, level="info"):
                    self.messaging_log_message(message, level=level)
                
                self.messaging_log_message("Opening LinkedIn messaging page...", level="info")
                open_messaging_page(self.driver)
                
                target_contacts = []
                if self.message_mode_var.get() == "broadcast":
                    self.messaging_log_message("Messaging all recent contacts", level="user")
                    target_contacts = self.contacts_data
                else:
                    for idx in selected_indices:
                        if idx < len(self.contacts_data):
                            target_contacts.append(self.contacts_data[idx])
                
                self.messaging_log_message(f"Sending messages to {len(target_contacts)} contacts", level="user")
                
                tone = self.message_tone_var.get()
                
                for i, (name, thread) in enumerate(target_contacts):
                    try:
                        self.messaging_log_message(f"Messaging contact: {name}", level="user")
                        
                        contact_message = message.replace("{name}", name).replace("{company}", "your company")
                        
                        self.messaging_log_message("Message content:", level="info")
                        self.messaging_log_message(contact_message, level="info")
                        
                        self.messaging_log_message(f"Sending message to {name}...", level="user")
                        success = send_message(self.driver, thread, name, contact_message, log_callback=log_callback, resume_path=resume_path)
                        
                        if success:
                            self.messaging_log_message(f"✅ Message sent to {name}", level="user")
                        else:
                            self.messaging_log_message(f"❌ Failed to send message to {name}", level="user")
                        
                        time.sleep(3)
                        
                    except Exception as e:
                        self.messaging_log_message(f"❌ Error messaging {name}: {e}", level="user")
                
                self.messaging_log_message("Messaging completed!", level="user")
                self.status_var.set("Finished bulk messaging")
                
            except Exception as e:
                error_msg = f"Error in messaging: {e}"
                self.status_var.set(error_msg)
                self.messaging_log_message(error_msg, level="user")
        
        long_operation(
            messaging_process, 
            self.status_var, 
            self.root,
            "Bulk messaging completed",
            "Error in bulk messaging"
        )
    
    def start_feed_interaction(self):
        if not self.check_login_status():
            return
        
        def feed_process():
            try:
                max_posts = self.max_posts_var.get()
                self.status_var.set(f"Starting feed interaction with {max_posts} posts...")
                self.feed_log_message(f"Starting feed interaction with {max_posts} posts...", clear=True, level="user")
                
                def log_callback(message, level="info"):
                    self.feed_log_message(message, level=level)
                
                engage_feed(self.driver, max_posts=max_posts, root=self.root, log_callback=log_callback)
                
                self.status_var.set("Finished feed interaction")
                self.feed_log_message("✅ Feed interaction completed", level="user")
                messagebox.showinfo("Success", "Feed interaction completed.")
            except Exception as e:
                self.status_var.set(f"Error in feed interaction: {e}")
                self.feed_log_message(f"❌ Error in feed interaction: {e}", level="user")
                messagebox.showerror("Error", f"Feed interaction failed: {e}")
        
        long_operation(
            feed_process, 
            self.status_var, 
            self.root,
            "Feed interaction completed",
            "Error in feed interaction"
        )
    
    def check_login_status(self):
        if not self.is_logged_in or not self.driver:
            messagebox.showerror("Error", "Please log in to LinkedIn first")
            self.status_var.set("Operation canceled: Not logged in")
            return False
        return True
    
    def on_closing(self):
        if self.driver:
            self.driver.quit()
        self.root.destroy()
    
    def connection_log_message(self, message, clear=False, level="info"):
        if level == "user":
            prefix = "✨ "
        elif level == "debug":
            prefix = "🔍 "
        else:
            prefix = ""
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if clear:
            self.connection_log_messages = []
            
        self.connection_log_messages.append((timestamp, message, level, prefix))
        
        selected_level = self.connection_log_level_var.get()
        show_message = False
        if selected_level == "debug":
            show_message = True
        elif selected_level == "info" and level != "debug":
            show_message = True
        elif selected_level == "user" and level == "user":
            show_message = True
        
        self.connection_log_text.config(state=tk.NORMAL)
        
        if clear:
            self.connection_log_text.delete(1.0, tk.END)
            
        if message and show_message:
            formatted_message = f"[{timestamp}] {prefix}{message}\n"
            self.connection_log_text.insert(tk.END, formatted_message)
            
        self.connection_log_text.see(tk.END)
        self.connection_log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_connection_log_display(self, event=None):
        selected_level = self.connection_log_level_var.get()
        
        self.connection_log_text.config(state=tk.NORMAL)
        self.connection_log_text.delete(1.0, tk.END)
        
        for timestamp, message, level, prefix in self.connection_log_messages:
            show = False
            if selected_level == "debug":
                show = True
            elif selected_level == "info" and level != "debug":
                show = True
            elif selected_level == "user" and level == "user":
                show = True
                
            if show:
                formatted_message = f"[{timestamp}] {prefix}{message}\n"
                self.connection_log_text.insert(tk.END, formatted_message)
        
        self.connection_log_text.config(state=tk.DISABLED)
        self.connection_log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = LinkedInAutomatorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()