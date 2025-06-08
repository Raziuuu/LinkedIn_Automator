# gui/utils.py (updated)
import tkinter as tk
from tkinter import ttk
import time

def create_tooltip(widget, text):
    tooltip = None
    def enter(event):
        nonlocal tooltip
        widget.update_idletasks()
        time.sleep(0.1)
        try:
            bbox = widget.bbox("insert")
            if bbox is None:
                x = widget.winfo_rootx() + 25
                y = widget.winfo_rooty() + 25
            else:
                x, y, _, _ = bbox
                x += widget.winfo_rootx() + 25
                y += widget.winfo_rooty() + 25
        except Exception:
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + 25
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
        label.pack()
    def leave(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

def create_scrollable_frame(parent):
    # Create a canvas that expands to fill the parent
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    frame = ttk.Frame(canvas)

    # Configure the canvas to expand
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill=tk.BOTH, expand=True)
    scrollbar.pack(side="right", fill=tk.Y)

    # Create a window in the canvas for the frame
    canvas_frame = canvas.create_window((0, 0), window=frame, anchor="nw")

    # Ensure the frame expands to fill the canvas width
    def configure_frame(event):
        canvas.itemconfig(canvas_frame, width=event.width)
    canvas.bind("<Configure>", configure_frame)

    # Update the scroll region when the frame size changes
    def configure_scrollregion(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind("<Configure>", configure_scrollregion)

    return canvas, frame

def long_operation(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper