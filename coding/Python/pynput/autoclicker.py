from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Listener as KeyboardListener
from pynput.keyboard import Controller as KeyboardController
from time import sleep
import threading

mouse = MouseController()
keyboard = KeyboardController()

toggled = False  # Whether the action loop is active
running = False  # Prevent multiple threads

def clickAndSendMessage():
    while toggled:
        # Save current mouse position
        original_position = mouse.position

        # Move and click first position
        mouse.position = (1700, 1000)
        sleep(0.1)
        mouse.click(Button.left, 1)

        # Type message
        keyboard.type("🌻" * 16)

        # Move and click second position
        mouse.position = (1880, 1000)
        sleep(0.1)
        mouse.click(Button.left, 1)

        # Return to original mouse position
        mouse.position = original_position

        sleep(0.1)  # Delay before repeating to avoid spam

def on_press(key):
    global toggled, running
    try:
        if key.char == 'z':
            toggled = not toggled  # Toggle on/off
            print(f"[Toggle] Action {'started' if toggled else 'stopped'}.")

            if toggled and not running:
                running = True
                threading.Thread(target=loop_wrapper, daemon=True).start()
    except AttributeError:
        pass

def loop_wrapper():
    global running
    clickAndSendMessage()
    running = False

# Start keyboard listener
with KeyboardListener(on_press=on_press) as listener:
    listener.join()
