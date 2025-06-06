from pynput import mouse

def on_click(x, y, button, pressed):
    print(f"Button: {button}, Pressed: {pressed}")

with mouse.Listener(on_click=on_click) as listener:
    print("Press mouse buttons (including side buttons)...")
    listener.join()
