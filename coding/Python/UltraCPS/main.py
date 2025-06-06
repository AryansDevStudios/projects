import customtkinter as ctk
from PIL import Image
from pynput.mouse import Button, Controller, Listener as MouseListener
from pynput import keyboard
import threading
import time
import random
import sys
import os

if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in normal Python
    base_path = os.path.abspath(".")

class IntEntry(ctk.CTkEntry):
    def __init__(self, *args, callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback
        self.var = ctk.StringVar()
        self.configure(textvariable=self.var, justify="center")
        self.var.trace_add("write", self.validate_int)
        self.bind("<FocusOut>", self.call_callback)
        self.bind("<Return>", self.call_callback)

    def validate_int(self, *_):
        value = self.var.get()
        if not value.isdigit() and value != "":
            self.var.set(''.join(filter(str.isdigit, value)))

    def call_callback(self, *_):
        if self.callback:
            self.callback(self.var.get())

activation_key = None
activation_key_type = None
listening_for_key = False
clicking = False
running = True
program_running = True

mouse = Controller()
temp_mouse_listener_instance = None

# Default CPS range
CPSmin = 20
CPSmax = 28

# Default Press Duration range in milliseconds
PressMinMS = 10   # corresponds to 0.010 s
PressMaxMS = 25   # corresponds to 0.025 s

def update_activation_button_text():
    if activation_key is None:
        btn_activation.configure(text="(none)")
    else:
        display_key = (
            activation_key.upper() if activation_key_type == "keyboard" else activation_key.lower()
        )
        btn_activation.configure(text=display_key)

def on_activation_button_click():
    global listening_for_key, temp_mouse_listener_instance, clicking
    if not program_running or listening_for_key:
        return
    listening_for_key = True
    clicking = False
    time.sleep(0.1)
    btn_activation.configure(text="Press any key...")
    app.bind("<Key>", on_key_press_for_config)
    temp_mouse_listener_instance = MouseListener(on_click=on_temp_mouse_click)
    temp_mouse_listener_instance.start()

def on_key_press_for_config(event):
    global activation_key, activation_key_type, listening_for_key, temp_mouse_listener_instance
    if not listening_for_key:
        return
    activation_key = event.keysym.lower()
    activation_key_type = "keyboard"
    listening_for_key = False
    app.unbind("<Key>")
    if temp_mouse_listener_instance and temp_mouse_listener_instance.is_alive():
        temp_mouse_listener_instance.stop()
    update_activation_button_text()

def on_temp_mouse_click(x, y, button, pressed):
    global activation_key, activation_key_type, listening_for_key, temp_mouse_listener_instance
    if not listening_for_key:
        return False
    if pressed:
        btn_str = str(button).split('.')[-1].lower()
        activation_key = btn_str
        activation_key_type = "mouse"
        listening_for_key = False
        app.unbind("<Key>")
        if temp_mouse_listener_instance and temp_mouse_listener_instance.is_alive():
            temp_mouse_listener_instance.stop()
        update_activation_button_text()
        return False
    return True

def get_button_from_string(s):
    s = s.lower()
    return Button.left if s == "left" else Button.right

def set_clicking_false():
    global clicking
    clicking = False

def click_loop():
    global clicking, running, CPSmin, CPSmax, PressMinMS, PressMaxMS

    while running:
        if not (program_running and clicking):
            time.sleep(0.001)
            continue

        # 1) Read CPS range safely
        try:
            min_cps_val = int(CPSmin)
            max_cps_val = int(CPSmax)
        except ValueError:
            min_cps_val = max_cps_val = 20

        if min_cps_val <= 0:
            min_cps_val = 1
        if max_cps_val < min_cps_val:
            max_cps_val = min_cps_val

        if min_cps_val == max_cps_val:
            target_cps = min_cps_val
        else:
            target_cps = random.randint(min_cps_val, max_cps_val)

        interval = 1.0 / target_cps

        # 2) Read Press‐Duration‐in‐ms range safely
        try:
            min_pd_ms = int(PressMinMS)
            max_pd_ms = int(PressMaxMS)
        except ValueError:
            min_pd_ms = 10
            max_pd_ms = 25

        if min_pd_ms <= 0:
            min_pd_ms = 1
        if max_pd_ms < min_pd_ms:
            max_pd_ms = min_pd_ms

        # Convert to seconds and pick random:
        if min_pd_ms == max_pd_ms:
            press_duration = min_pd_ms / 1000.0
        else:
            press_duration = random.uniform(min_pd_ms / 1000.0, max_pd_ms / 1000.0)

        btn_type = get_button_from_string(dropdown_click_type.get())

        start_time = time.perf_counter()

        # 3) Perform the click:
        mouse.press(btn_type)
        time.sleep(press_duration)
        mouse.release(btn_type)

        # 4) Optional “Circle” jitter:
        if dropdown_jitter_mode.get() == "Circle":
            try:
                radius = int(entry_jitter_radius.var.get() or "0")
            except ValueError:
                radius = 0

            if radius > 0:
                ox, oy = mouse.position
                jitter_x = random.randint(-radius, radius)
                jitter_y = random.randint(-radius, radius)
                mouse.move(jitter_x, jitter_y)
                # (No extra sleep here; assume minimal cost)
                mouse.move(-jitter_x, -jitter_y)

        # 5) Sleep until next interval tick:
        elapsed = time.perf_counter() - start_time
        remaining = interval - elapsed
        if remaining > 0:
            time.sleep(remaining)
        else:
            # We're behind schedule — skip sleeping to catch up
            pass

def on_keyboard_press(key):
    global clicking
    if not program_running or activation_key_type != "keyboard" or activation_key is None or listening_for_key:
        return True
    try:
        if hasattr(key, "char") and key.char is not None:
            kname = key.char.lower()
        elif hasattr(key, "name"):
            kname = key.name.lower()
        else:
            return True
        if kname == activation_key:
            mode = dropdown_click_mode.get().lower()
            if mode == "hold":
                clicking = True
            elif mode == "toggle":
                clicking = not clicking
    except Exception as e:
        print("Keyboard listener error:", e)
    return True

def on_keyboard_release(key):
    global clicking
    if not program_running or activation_key_type != "keyboard" or activation_key is None or listening_for_key:
        return True
    if dropdown_click_mode.get().lower() == "hold":
        try:
            kname = ""
            if hasattr(key, "char") and key.char is not None:
                kname = key.char.lower()
            elif hasattr(key, "name"):
                kname = key.name.lower()
            else:
                return True

            if kname == activation_key:
                threading.Timer(0.05, set_clicking_false).start()
        except Exception as e:
            print("Keyboard listener release error:", e)
    return True

def on_mouse_click(x, y, button, pressed):
    global clicking
    if not program_running or activation_key_type != "mouse" or activation_key is None or listening_for_key:
        return True

    btn_str = str(button).split('.')[-1].lower()
    if btn_str != activation_key:
        return True

    mode = dropdown_click_mode.get().lower()
    if pressed:
        if mode == "hold":
            clicking = True
        elif mode == "toggle":
            clicking = not clicking
    else:
        if mode == "hold":
            threading.Timer(0.05, set_clicking_false).start()
    return True

def on_click_mode_change(value):
    update_activation_button_text()

def on_jitter_mode_change(value):
    pass

def on_click_type_change(value):
    pass

def on_jitter_radius_change(value):
    pass

def on_min_cps_change(value):
    global CPSmin
    try:
        CPSmin = int(value)
        if CPSmin > CPSmax:
            CPSmin = CPSmax
            entry_min_cps.var.set(str(CPSmin))
    except:
        pass

def on_max_cps_change(value):
    global CPSmax
    try:
        CPSmax = int(value)
        if CPSmax < CPSmin:
            CPSmax = CPSmin
            entry_max_cps.var.set(str(CPSmax))
    except:
        pass

# New callbacks for Press Duration (ms):
def on_min_press_change(value):
    global PressMinMS, PressMaxMS
    try:
        PressMinMS = int(value)
        if PressMinMS > PressMaxMS:
            PressMinMS = PressMaxMS
            entry_min_press.var.set(str(PressMinMS))
    except:
        pass

def on_max_press_change(value):
    global PressMinMS, PressMaxMS
    try:
        PressMaxMS = int(value)
        if PressMaxMS < PressMinMS:
            PressMaxMS = PressMinMS
            entry_max_press.var.set(str(PressMaxMS))
    except:
        pass

def defocus_entries(event):
    event.widget.focus_set()

def on_master_toggle():
    global program_running, clicking
    program_running = not program_running
    if program_running:
        btn_master.configure(text="Stop Program", fg_color="#ef4444", hover_color="#b91c1c")
        clicking = False
        time.sleep(0.1)
    else:
        clicking = False
        time.sleep(0.1)
        btn_master.configure(text="Start Program", fg_color="#22c55e", hover_color="#16a34a")

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("660x650")
app.title("CPS Clicker")
icon_path = os.path.join(base_path, "assets", "iconMain.ico")
img_label_path = os.path.join(base_path, "assets", "guiDisplayIcon.png")

app.iconbitmap(icon_path)

image = ctk.CTkImage(
    light_image=Image.open(img_label_path),
    size=(280, 70)
)
img_label = ctk.CTkLabel(app, image=image, text="")
img_label.pack(pady=25)

app.bind("<Button-1>", defocus_entries)

# --- GUI rows ---

# Row 1: Activation key configuration
row1 = ctk.CTkFrame(app, fg_color="transparent")
row1.pack(fill="x", padx=20, pady=8)

label_activation = ctk.CTkLabel(
    row1,
    text="Configure button to activate",
    font=("Arial", 24),
    anchor="w",
    width=400
)
label_activation.pack(side="left")
ctk.CTkLabel(row1, text="").pack(side="left", expand=True)

btn_activation = ctk.CTkButton(
    row1,
    text="(none)",
    width=240,
    height=30,
    corner_radius=10,
    fg_color="#3b82f6",
    hover_color="#2563eb",
    font=("Arial", 20),
    text_color="white",
    command=on_activation_button_click
)
btn_activation.pack(side="right")

# Row 2: Click activation mode
row2 = ctk.CTkFrame(app, fg_color="transparent")
row2.pack(fill="x", padx=20, pady=8)

label_click_mode = ctk.CTkLabel(
    row2,
    text="Click activation mode",
    font=("Arial", 24),
    anchor="w",
    width=400
)
label_click_mode.pack(side="left")
ctk.CTkLabel(row2, text="").pack(side="left", expand=True)

dropdown_click_mode = ctk.CTkOptionMenu(
    row2,
    values=["Hold", "Toggle"],
    width=240,
    height=30,
    corner_radius=10,
    fg_color="#3b82f6",
    button_color="#3b82f6",
    button_hover_color="#2563eb",
    dropdown_fg_color="#3b82f6",
    dropdown_hover_color="#2563eb",
    dropdown_text_color="white",
    font=("Arial", 20),
    dropdown_font=("Arial", 20),
    text_color="white",
    command=on_click_mode_change
)
dropdown_click_mode.set("Hold")
dropdown_click_mode.pack(side="right")

# Row 3: Jitter mode
row3 = ctk.CTkFrame(app, fg_color="transparent")
row3.pack(fill="x", padx=20, pady=8)

label_jitter_mode = ctk.CTkLabel(
    row3,
    text="Jitter mode",
    font=("Arial", 24),
    anchor="w",
    width=400
)
label_jitter_mode.pack(side="left")
ctk.CTkLabel(row3, text="").pack(side="left", expand=True)

dropdown_jitter_mode = ctk.CTkOptionMenu(
    row3,
    values=["Disabled", "Circle"],
    width=240,
    height=30,
    corner_radius=10,
    fg_color="#3b82f6",
    button_color="#3b82f6",
    button_hover_color="#2563eb",
    dropdown_fg_color="#3b82f6",
    dropdown_hover_color="#2563eb",
    dropdown_text_color="white",
    font=("Arial", 20),
    dropdown_font=("Arial", 20),
    text_color="white",
    command=on_jitter_mode_change
)
dropdown_jitter_mode.set("Disabled")
dropdown_jitter_mode.pack(side="right")

# Row 4: Jitter radius
row4 = ctk.CTkFrame(app, fg_color="transparent")
row4.pack(fill="x", padx=20, pady=8)

label_jitter_radius = ctk.CTkLabel(
    row4,
    text="Jitter radius",
    font=("Arial", 24),
    anchor="w",
    width=400
)
label_jitter_radius.pack(side="left")
ctk.CTkLabel(row4, text="").pack(side="left", expand=True)

entry_jitter_radius = IntEntry(
    row4,
    width=240,
    height=30,
    font=("Arial", 20),
    callback=on_jitter_radius_change
)
entry_jitter_radius.insert(0, "3")
entry_jitter_radius.pack(side="right")

# Row 5: Click type (Left/Right)
row5 = ctk.CTkFrame(app, fg_color="transparent")
row5.pack(fill="x", padx=20, pady=8)

label_click_type = ctk.CTkLabel(
    row5,
    text="Click type",
    font=("Arial", 24),
    anchor="w",
    width=400
)
label_click_type.pack(side="left")
ctk.CTkLabel(row5, text="").pack(side="left", expand=True)

dropdown_click_type = ctk.CTkOptionMenu(
    row5,
    values=["Left", "Right"],
    width=240,
    height=30,
    corner_radius=10,
    fg_color="#3b82f6",
    button_color="#3b82f6",
    button_hover_color="#2563eb",
    dropdown_fg_color="#3b82f6",
    dropdown_hover_color="#2563eb",
    dropdown_text_color="white",
    font=("Arial", 20),
    dropdown_font=("Arial", 20),
    text_color="white",
    command=on_click_type_change
)
dropdown_click_type.set("Left")
dropdown_click_type.pack(side="right")

# Row 6: Min CPS
row6 = ctk.CTkFrame(app, fg_color="transparent")
row6.pack(fill="x", padx=20, pady=8)

label_min_cps = ctk.CTkLabel(
    row6,
    text="Min CPS",
    font=("Arial", 24),
    anchor="w",
    width=400
)
label_min_cps.pack(side="left")
ctk.CTkLabel(row6, text="").pack(side="left", expand=True)

entry_min_cps = IntEntry(
    row6,
    width=240,
    height=30,
    font=("Arial", 20),
    callback=on_min_cps_change
)
entry_min_cps.insert(0, "20")
entry_min_cps.pack(side="right")

# Row 7: Max CPS
row7 = ctk.CTkFrame(app, fg_color="transparent")
row7.pack(fill="x", padx=20, pady=8)

label_max_cps = ctk.CTkLabel(
    row7,
    text="Max CPS",
    font=("Arial", 24),
    anchor="w",
    width=400
)
label_max_cps.pack(side="left")
ctk.CTkLabel(row7, text="").pack(side="left", expand=True)

entry_max_cps = IntEntry(
    row7,
    width=240,
    height=30,
    font=("Arial", 20),
    callback=on_max_cps_change
)
entry_max_cps.insert(0, "28")
entry_max_cps.pack(side="right")

# Row 8: Min Press Duration (ms)
row8 = ctk.CTkFrame(app, fg_color="transparent")
row8.pack(fill="x", padx=20, pady=8)

label_min_press = ctk.CTkLabel(
    row8,
    text="Min Press (ms)",
    font=("Arial", 24),
    anchor="w",
    width=400
)
label_min_press.pack(side="left")
ctk.CTkLabel(row8, text="").pack(side="left", expand=True)

entry_min_press = IntEntry(
    row8,
    width=240,
    height=30,
    font=("Arial", 20),
    callback=on_min_press_change
)
entry_min_press.insert(0, "10")  # default 10 ms
entry_min_press.pack(side="right")

# Row 9: Max Press Duration (ms)
row9 = ctk.CTkFrame(app, fg_color="transparent")
row9.pack(fill="x", padx=20, pady=8)

label_max_press = ctk.CTkLabel(
    row9,
    text="Max Press (ms)",
    font=("Arial", 24),
    anchor="w",
    width=400
)
label_max_press.pack(side="left")
ctk.CTkLabel(row9, text="").pack(side="left", expand=True)

entry_max_press = IntEntry(
    row9,
    width=240,
    height=30,
    font=("Arial", 20),
    callback=on_max_press_change
)
entry_max_press.insert(0, "25")  # default 25 ms
entry_max_press.pack(side="right")

# --- Master Toggle Button at Bottom Center ---
btn_master = ctk.CTkButton(
    app,
    text="Stop Program",
    width=240,
    height=50,
    corner_radius=12,
    fg_color="#ef4444",  # Red when running
    hover_color="#b91c1c",
    font=("Arial", 24),
    text_color="white",
    command=on_master_toggle
)
btn_master.pack(pady=25)

update_activation_button_text()

# --- Start click loop thread ---
threading.Thread(target=click_loop, daemon=True).start()

# --- Global keyboard and mouse listeners ---
keyboard_listener = keyboard.Listener(on_press=on_keyboard_press, on_release=on_keyboard_release)
keyboard_listener.start()

mouse_listener = MouseListener(on_click=on_mouse_click)
mouse_listener.start()

# Start the GUI event loop
app.mainloop()

# Cleanup after window is closed
running = False
keyboard_listener.stop()
mouse_listener.stop()
