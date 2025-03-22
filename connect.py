import threading
import time
import tkinter as tk
from tkinter import ttk, font
from functools import partial

# Import your modified modules (make sure you've added global key mapping variables)
import npg1  # should define key_left_npg1 and key_right_npg1
import npg2  # should define key_left_npg2 and key_right_npg2

# Store the new mapping values in a dictionary
key_mappings = {
    "npg1_left": npg1.key_left_npg1,
    "npg1_right": npg1.key_right_npg1,
    "npg2_left": npg2.key_left_npg2,
    "npg2_right": npg2.key_right_npg2,
}

# Helper function for key mapping
def on_mapping_click(mapping_name, button):
    # Visual feedback for active mapping
    for btn in all_mapping_buttons:
        btn.config(style="TButton")
    button.config(style="Active.TButton")
    button.config(text="Press a key...")

    def key_handler(event):
        # Use event.char if available; if not, fallback to the key symbol
        key = event.char if event.char != "" else event.keysym
        key_mappings[mapping_name] = key
        button.config(text=key)
        button.config(style="TButton")
        # Unbind the key handler so only the first key press is captured
        root.unbind("<Key>")
        return "break"

    # Bind the key press event on the root window
    root.bind("<Key>", key_handler)

# Function to update the module-level key mappings and start the BLE threads
def start_scripts():
    # Update the key mappings for both modules
    npg1.key_left_npg1 = key_mappings["npg1_left"]
    npg1.key_right_npg1 = key_mappings["npg1_right"]
    npg2.key_left_npg2 = key_mappings["npg2_left"]
    npg2.key_right_npg2 = key_mappings["npg2_right"]

    # Disable the mapping buttons and start button
    for btn in all_mapping_buttons:
        btn.config(state=tk.DISABLED)
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

    # Update status
    status_label.config(text="Scripts running", foreground="#4CAF50")
    status_indicator.config(bg="#4CAF50")
    
    # Start the BLE threads from both scripts in separate daemon threads
    global thread1, thread2, running
    running = True
    thread1 = threading.Thread(target=npg1.ble_thread, daemon=True)
    thread2 = threading.Thread(target=npg2.ble_thread, daemon=True)
    thread1.start()
    thread2.start()

# Function to stop running scripts
def stop_scripts():
    global running
    running = False
    
    # This assumes your ble_thread functions can be stopped by setting a flag
    # You might need to modify your original modules to support this
    
    # Re-enable the mapping buttons and start button
    for btn in all_mapping_buttons:
        btn.config(state=tk.NORMAL)
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    
    # Update status
    status_label.config(text="Scripts stopped", foreground="#F44336")
    status_indicator.config(bg="#F44336")

# Toggle always on top
def toggle_always_on_top():
    current_state = root.attributes('-topmost')
    root.attributes('-topmost', not current_state)
    if not current_state:
        pin_button.config(text="📌 Unpin Window")
    else:
        pin_button.config(text="📌 Pin Window")

# Build the UI
root = tk.Tk()
root.title("NPG Key Mapper")
root.configure(bg="#f5f5f5")
root.resizable(False, False)

# Set a nice icon (replace with your own if available)
try:
    root.iconbitmap("key_icon.ico")  # Replace with path to your icon
except:
    pass  # No icon available, continue without it

# Define custom styles
style = ttk.Style()
style.theme_use('clam')  # Use a modern theme as base

# Configure colors
bg_color = "#f5f5f5"
accent_color = "#2196F3"
hover_color = "#1976D2"
section_bg = "#ffffff"

style.configure("TFrame", background=bg_color)
style.configure("Section.TFrame", background=section_bg, relief="solid", borderwidth=1)
style.configure("TLabel", background=bg_color, font=('Segoe UI', 10))
style.configure("Section.TLabel", background=section_bg, font=('Segoe UI', 10))
style.configure("Header.TLabel", background=bg_color, font=('Segoe UI', 12, 'bold'))
style.configure("Status.TLabel", background=bg_color, font=('Segoe UI', 9))

# Button styles
style.configure("TButton", 
                background=accent_color,
                foreground="black",
                font=('Segoe UI', 10),
                padding=5)

style.configure("Active.TButton", 
                background="#FFC107",
                foreground="black",
                font=('Segoe UI', 10, 'bold'),
                padding=5)

style.configure("Start.TButton", 
                background="#4CAF50",
                foreground="white",
                font=('Segoe UI', 10, 'bold'),
                padding=8)

style.configure("Stop.TButton", 
                background="#F44336",
                foreground="white",
                font=('Segoe UI', 10, 'bold'),
                padding=8)

style.configure("Pin.TButton", 
                background=bg_color,
                font=('Segoe UI', 9),
                padding=2)

# Main container
main_frame = ttk.Frame(root, padding="15", style="TFrame")
main_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))

# Header
header_frame = ttk.Frame(main_frame, style="TFrame")
header_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

app_title = ttk.Label(header_frame, text="BLE Key Mapper", style="Header.TLabel")
app_title.grid(row=0, column=0, sticky=tk.W)

pin_button = ttk.Button(header_frame, text="📌 Pin Window", command=toggle_always_on_top, style="Pin.TButton")
pin_button.grid(row=0, column=1, sticky=tk.E, padx=(50, 0))

# NPG1 Section
npg1_frame = ttk.Frame(main_frame, padding="10", style="Section.TFrame")
npg1_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5), pady=(0, 10))

npg1_title = ttk.Label(npg1_frame, text="NPG1 Device", font=('Segoe UI', 11, 'bold'), style="Section.TLabel")
npg1_title.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

ttk.Label(npg1_frame, text="Gesture 1:", style="Section.TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
btn_npg1_left = ttk.Button(npg1_frame, text=key_mappings["npg1_left"], width=10)
btn_npg1_left.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
btn_npg1_left.config(command=partial(on_mapping_click, "npg1_left", btn_npg1_left))

ttk.Label(npg1_frame, text="Gesture 2:", style="Section.TLabel").grid(row=2, column=0, sticky=tk.W, pady=5)
btn_npg1_right = ttk.Button(npg1_frame, text=key_mappings["npg1_right"], width=10)
btn_npg1_right.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
btn_npg1_right.config(command=partial(on_mapping_click, "npg1_right", btn_npg1_right))

# NPG2 Section
npg2_frame = ttk.Frame(main_frame, padding="10", style="Section.TFrame")
npg2_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0), pady=(0, 10))

npg2_title = ttk.Label(npg2_frame, text="NPG2 Device", font=('Segoe UI', 11, 'bold'), style="Section.TLabel")
npg2_title.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

ttk.Label(npg2_frame, text="Gesture 2:", style="Section.TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
btn_npg2_left = ttk.Button(npg2_frame, text=key_mappings["npg2_left"], width=10)
btn_npg2_left.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
btn_npg2_left.config(command=partial(on_mapping_click, "npg2_left", btn_npg2_left))

ttk.Label(npg2_frame, text="Gesture 2:", style="Section.TLabel").grid(row=2, column=0, sticky=tk.W, pady=5)
btn_npg2_right = ttk.Button(npg2_frame, text=key_mappings["npg2_right"], width=10)
btn_npg2_right.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
btn_npg2_right.config(command=partial(on_mapping_click, "npg2_right", btn_npg2_right))

# Store all mapping buttons for easy access
all_mapping_buttons = [btn_npg1_left, btn_npg1_right, btn_npg2_left, btn_npg2_right]

# Control buttons frame
control_frame = ttk.Frame(main_frame, style="TFrame")
control_frame.grid(row=2, column=0, columnspan=2, pady=(10, 5))

# Start and Stop buttons
start_button = ttk.Button(control_frame, text="▶ Start", command=start_scripts, style="Start.TButton", width=12)
start_button.grid(row=0, column=0, padx=5)

stop_button = ttk.Button(control_frame, text="◼ Stop", command=stop_scripts, style="Stop.TButton", width=12)
stop_button.grid(row=0, column=1, padx=5)
stop_button.config(state=tk.DISABLED)

# Status frame
status_frame = ttk.Frame(main_frame, style="TFrame")
status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

status_indicator = tk.Canvas(status_frame, width=12, height=12, bg="#F44336", highlightthickness=0)
status_indicator.grid(row=0, column=0, padx=(0, 5))

status_label = ttk.Label(status_frame, text="Ready", style="Status.TLabel")
status_label.grid(row=0, column=1, sticky=tk.W)

# Global variables for thread management
thread1 = None
thread2 = None
running = False

# Center the window on screen
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{width}x{height}+{x}+{y}')

# Start with always on top enabled
root.attributes('-topmost', True)

root.mainloop()

# Clean exit - likely never reached due to daemon threads