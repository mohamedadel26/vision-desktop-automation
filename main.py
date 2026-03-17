import pyautogui
import time
import os
from automation.grounding import IconGrounder
from automation.desktop import (
    open_notepad, 
    go_to_desktop, 
    is_notepad_window_active,
    get_window_title
)
from automation.api import get_posts
from automation.notepad import write_post, save_post, close_notepad


def find_icon_retry(grounder, max_attempts=3, delay=1):
    """
    Try to find the icon with retry logic
    
    Args:
        grounder: IconGrounder instance
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
        
    Returns:
        tuple: (x, y) coordinates or None if not found
    """
    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Attempt {attempt}/{max_attempts} ---")
        
        pos = grounder.find_icon()
        
        if pos:
            print(f"✓ Icon found at: {pos}")
            return pos
        
        print(f"✗ Icon not found on attempt {attempt}")
        
        if attempt < max_attempts:
            print(f"Retrying in {delay} second(s)...")
            time.sleep(delay)
    
    return None


def validate_notepad_launch():
    """
    Validate that Notepad was successfully launched
    
    Returns:
        bool: True if Notepad is running
    """
    print("Validating Notepad launch...")
    
    # Method 1: Check window title
    title = get_window_title()
    if title and "notepad" in title.lower():
        print(f"✓ Notepad detected: '{title}'")
        return True
    
    # Method 2: Wait and check again
    if is_notepad_window_active(timeout=3):
        print("✓ Notepad window detected")
        return True
    
    # Method 3: If no window detection available, assume success after waiting
    if title is None:
        print("⚠ Window detection unavailable, assuming Notepad opened")
        time.sleep(1)
        return True
    
    print("✗ Notepad validation failed")
    return False

def clear_mouse_hover():
    w, h = pyautogui.size()
    pyautogui.moveTo(w - 10, h - 10, duration=0.2)

def run():
    """
    Main automation workflow
    """
    print("=" * 60)
    print("Vision-Based Desktop Automation - Starting")
    print("=" * 60)
    
    # Ensure output directory exists
    output_dir = os.path.expanduser("~/Desktop/tjm-project")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Create icon detector with debug mode
    print("\nInitializing Icon Grounder...")
    grounder = IconGrounder("icons/notepad.png", debug=True)
    
    # Go to desktop to see icons
    print("\nGoing to desktop...")
    go_to_desktop()
    time.sleep(1)
    
    # Fetch posts from API
    print("\nFetching posts from API...")
    posts = get_posts()
    
    if not posts:
        print("ERROR: No posts fetched from API. Exiting.")
        return
    
    print(f"✓ Fetched {len(posts)} posts")
    
    # Process each post
    print("\n" + "=" * 60)
    print("Starting automation loop")
    print("=" * 60)
    
    for i, post in enumerate(posts, 1):
        print(f"\n{'=' * 40}")
        print(f"Processing post {i}/10 (ID: {post['id']})")
        print(f"{'=' * 40}")
        
        # Find the Notepad icon
        pos = find_icon_retry(grounder, max_attempts=3, delay=1)
        
        if not pos:
            print(f"ERROR: Could not find Notepad icon for post {post['id']}")
            print("Taking screenshot for debugging...")
            grounder.screenshot()
            continue
        
        x, y = pos
        print(f"Clicking Notepad icon at ({x}, {y})")
        
        # Open Notepad
        open_notepad(x, y)
        
        # Validate Notepad opened
        if not validate_notepad_launch():
            print("WARNING: Notepad may not have opened properly")
            # Try to continue anyway
        
        # Write post content
        print(f"Writing post content...")
        write_post(post)
        
        # Save the file
        print(f"Saving as post_{post['id']}.txt...")
        save_post(post["id"])
        
        # Close Notepad
        print("Closing Notepad...")
        close_notepad()
        # pyautogui.moveTo(1063, 350, duration=0.1)
        clear_mouse_hover()
        time.sleep(0.1)
        # Brief pause before next iteration
        time.sleep(1)
        
        # Go back to desktop for next iteration
        go_to_desktop()
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("Automation completed!")
    print(f"Files saved to: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()