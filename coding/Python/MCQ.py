from pynput.mouse import Listener
import pyperclip
import threading
import time

mouse_position = (0, 0)

# Constantly print current position
def show_position():
    while True:
        print(f"Current Position: {mouse_position}", end="\r")
        time.sleep(0.1)

# On move, update the global position
def on_move(x, y):
    global mouse_position
    mouse_position = (x, y)

# On click, copy to clipboard
def on_click(x, y, button, pressed):
    if pressed and button.name == "left":
        coord_str = f"{x}, {y}"
        pyperclip.copy(coord_str)
        print(f"\nCopied to clipboard: {coord_str}")

# Start position printing in background
threading.Thread(target=show_position, daemon=True).start()

# Start mouse listener
with Listener(on_move=on_move, on_click=on_click) as listener:
    listener.join()
