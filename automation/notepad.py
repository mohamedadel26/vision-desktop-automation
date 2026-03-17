import pyautogui
import time
import os
from pathlib import Path

def write_post(post):
    """Write the post content to Notepad"""
    text = f"Title: {post['title']}\n\n{post['body']}"
    pyautogui.write(text, interval=0.01)

def save_post(post_id):

    target_dir = Path.home() / "Desktop" / "tjm-project"
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {target_dir}")

    file_path = target_dir / f"post_{post_id}.txt"
    file_path_str = str(file_path.resolve()) 

    file_exists = file_path.exists()
    if file_exists:
        print(f"Warning: {file_path_str} exists, will overwrite")

    pyautogui.hotkey("ctrl", "s")
    time.sleep(1)  

    pyautogui.write(file_path_str, interval=0.01)
    time.sleep(0.5)

    pyautogui.press("enter")
    time.sleep(1)

    if file_exists:
        time.sleep(0.3)
        pyautogui.press("y")  
        time.sleep(0.5)

    time.sleep(1)

def close_notepad():
    """
    Close Notepad window properly - single attempt only
    """
    # Press Alt+F4 once to close
    pyautogui.hotkey("alt", "f4")
    time.sleep(0.5)
    
    # If "Save changes?" dialog appears, press 'n' for Don't Save
    pyautogui.press("n")
    time.sleep(0.5)


