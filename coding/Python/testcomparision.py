import win32api, win32con  # type: ignore
import keyboard
import threading
import time

show_pos = True

optionA = (1800, 220)
optionB = (1800, 290)
optionC = (1800, 360)
optionD = (1800, 430)

submitButton = (1800, 990)

def monitor_keys():
    while True:
        initialPos=win32api.GetCursorPos()
        if keyboard.is_pressed("1"):
            print("Pressed option A.")
            win32api.SetCursorPos(optionA)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

            win32api.SetCursorPos(submitButton)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

            win32api.SetCursorPos(initialPos)

        elif keyboard.is_pressed("2"):
            print("Pressed option B.")
            win32api.SetCursorPos(optionB)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

            win32api.SetCursorPos(submitButton)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

            win32api.SetCursorPos(initialPos)

        elif keyboard.is_pressed("3"):
            print("Pressed option C.")
            win32api.SetCursorPos(optionC)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)  

            win32api.SetCursorPos(submitButton)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

            win32api.SetCursorPos(initialPos)

        elif keyboard.is_pressed("4"):
            print("Pressed option D.")
            win32api.SetCursorPos(optionD)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

            win32api.SetCursorPos(submitButton)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

            win32api.SetCursorPos(initialPos)
            
        time.sleep(0.005)



threading.Thread(target=monitor_keys).start()       