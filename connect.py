import threading
import time
import tkinter as tk
from tkinter import ttk

# Import your modified modules (make sure you've added global key mapping variables)
import npg1  # should define key_left_npg1 and key_right_npg1
import npg2  # should define key_left_npg2 and key_right_npg2

# We'll store the new mapping values in a dictionary
key_mappings = {
    "npg1_left": npg1.key_left_npg1,
    "npg1_right": npg1.key_right_npg1,
    "npg2_left": npg2.key_left_npg2,
    "npg2_right": npg2.key_right_npg2,
}

# A helper function that will be called when a mapping button is clicked.
# It changes the button text to "Press a key..." and binds a one-time key event.
def on_mapping_click(mapping_name, button):
    button.config(text="Press a key...")

    def key_handler(event):
        # Use event.char if available; if not, fallback to the key symbol.
        key = event.char if event.char != "" else event.keysym
        key_mappings[mapping_name] = key
        button.config(text=key)
        # Unbind the key handler so only the first key press is captured.
        root.unbind("<Key>")
        return "break"

    # Bind the key press event on the root window.
    root.bind("<Key>", key_handler)

# The start_scripts function will update the module-level key mappings and then start the BLE threads.
def start_scripts():
    # Update the key mappings for npg1
    npg1.key_left_npg1 = key_mappings["npg1_left"]
    npg1.key_right_npg1 = key_mappings["npg1_right"]

    # Update the key mappings for npg2
    npg2.key_left_npg2 = key_mappings["npg2_left"]
    npg2.key_right_npg2 = key_mappings["npg2_right"]

    # Disable the mapping buttons and start button since we are now running the scripts.
    btn_npg1_left.config(state=tk.DISABLED)
    btn_npg1_right.config(state=tk.DISABLED)
    btn_npg2_left.config(state=tk.DISABLED)
    btn_npg2_right.config(state=tk.DISABLED)
    start_button.config(state=tk.DISABLED)

    # Start the BLE threads from both scripts in separate daemon threads.
    thread1 = threading.Thread(target=npg1.ble_thread, daemon=True)
    thread2 = threading.Thread(target=npg2.ble_thread, daemon=True)
    thread1.start()
    thread2.start()
    status_label.config(text="Scripts running...", foreground="green")

# Build the UI
root = tk.Tk()
root.title("Key Mapper for npg1 and npg2")

mainframe = ttk.Frame(root, padding="10")
mainframe.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))

# Create mapping buttons for npg1
ttk.Label(mainframe, text="npg1 Left Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
btn_npg1_left = ttk.Button(mainframe, text=key_mappings["npg1_left"],
                           command=lambda: on_mapping_click("npg1_left", btn_npg1_left))
btn_npg1_left.grid(row=0, column=1, sticky=tk.W, padx=5)

ttk.Label(mainframe, text="npg1 Right Key:").grid(row=1, column=0, sticky=tk.W, pady=5)
btn_npg1_right = ttk.Button(mainframe, text=key_mappings["npg1_right"],
                            command=lambda: on_mapping_click("npg1_right", btn_npg1_right))
btn_npg1_right.grid(row=1, column=1, sticky=tk.W, padx=5)

# Create mapping buttons for npg2
ttk.Label(mainframe, text="npg2 Left Key:").grid(row=2, column=0, sticky=tk.W, pady=5)
btn_npg2_left = ttk.Button(mainframe, text=key_mappings["npg2_left"],
                           command=lambda: on_mapping_click("npg2_left", btn_npg2_left))
btn_npg2_left.grid(row=2, column=1, sticky=tk.W, padx=5)

ttk.Label(mainframe, text="npg2 Right Key:").grid(row=3, column=0, sticky=tk.W, pady=5)
btn_npg2_right = ttk.Button(mainframe, text=key_mappings["npg2_right"],
                            command=lambda: on_mapping_click("npg2_right", btn_npg2_right))
btn_npg2_right.grid(row=3, column=1, sticky=tk.W, padx=5)

# Start button to launch both scripts.
start_button = ttk.Button(mainframe, text="Start", command=start_scripts)
start_button.grid(row=4, column=0, columnspan=2, pady=15)

status_label = ttk.Label(mainframe, text="")
status_label.grid(row=5, column=0, columnspan=2)

root.mainloop()

# Optionally, keep the main thread alive
while True:
    time.sleep(0.1)
