import pyautogui
import time

# Try to import win32gui for window detection (optional)
try:
    import win32gui
    HAS_WIN32GUI = True
except ImportError:
    HAS_WIN32GUI = False
    print("Warning: win32gui not available, using fallback detection")



def go_to_desktop():
    """Press Windows + D to go to desktop"""
    pyautogui.hotkey("winleft", "d")
    time.sleep(1)

# START_X = 1063
# START_Y = 350

def open_notepad(x, y):
    """Open Notepad by double-clicking at the given coordinates"""
    # pyautogui.moveTo(START_X, START_Y, duration=0.1)
    # Move to position
    pyautogui.moveTo(x, y, duration=0.3)
    time.sleep(0.2)
    
    # Double click to open Notepad
    pyautogui.doubleClick()
    time.sleep(2)

def is_notepad_window_active(timeout=5):
    """Check if Notepad window is active"""
    if not HAS_WIN32GUI:
        time.sleep(timeout)
        return True
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                window_title = win32gui.GetWindowText(hwnd)
                if window_title and "notepad" in window_title.lower():
                    return True
        except:
            pass
        time.sleep(0.5)
    return False

def get_window_title():
    """Get the title of the currently active window"""
    if not HAS_WIN32GUI:
        return None
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            return win32gui.GetWindowText(hwnd)
    except:
        pass
    return None

def minimize_window():
    """Minimize the current window"""
    pyautogui.hotkey("winleft", "down")
    time.sleep(0.3)

