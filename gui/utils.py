import tkinter as tk
from tkinter import ttk
import threading
import time

def create_tooltip(widget, text):
    """
    Create a tooltip for a given widget
    """
    def enter(event):
        # Get widget position
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 20
        
        # Create a toplevel window
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create label
        label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack(ipadx=5, ipady=5)
        
        widget.tooltip = tooltip
        
    def leave(event):
        if hasattr(widget, "tooltip"):
            widget.tooltip.destroy()
            
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

def long_operation(callback, status_var=None, root=None, success_msg="Operation completed", error_msg="Operation failed"):
    """
    Run a long operation in a separate thread and update status
    
    Args:
        callback: Function to run in the thread
        status_var: StringVar to update with status messages
        root: Tk root for updating UI
        success_msg: Message to show on success
        error_msg: Message to show on error
    """
    def thread_function():
        try:
            if status_var and root:
                status_var.set("Operation in progress...")
                root.update_idletasks()
                
            callback()
            
            if status_var and root:
                status_var.set(success_msg)
                root.update_idletasks()
        except Exception as e:
            if status_var and root:
                status_var.set(f"{error_msg}: {e}")
                root.update_idletasks()
    
    threading.Thread(target=thread_function, daemon=True).start()

def create_scrollable_frame(parent):
    """
    Create a scrollable frame
    
    Returns:
        outer_frame: The container frame with scrollbars
        inner_frame: The frame where you should place your widgets
    """
    # Create a canvas with scrollbar
    outer_frame = ttk.Frame(parent)
    canvas = tk.Canvas(outer_frame)
    scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
    
    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Create a frame inside the canvas
    inner_frame = ttk.Frame(canvas)
    inner_frame_id = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
    
    # Update the scrollregion when the inner frame size changes
    def configure_inner_frame(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Update the canvas window when the canvas size changes
    def configure_canvas(event):
        canvas.itemconfig(inner_frame_id, width=event.width)
    
    inner_frame.bind("<Configure>", configure_inner_frame)
    canvas.bind("<Configure>", configure_canvas)
    
    return outer_frame, inner_frame 