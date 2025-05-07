import os
import time
import pyautogui
from datetime import datetime
import config

def take_screenshot():
    """Take a screenshot and save it to the screenshots directory."""
    # Create screenshots directory if it doesn't exist
    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
    
    # Generate a filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(config.SCREENSHOT_DIR, filename)
    
    # Take the screenshot
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    
    return filepath
