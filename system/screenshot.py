import os
import time
import pyautogui
from datetime import datetime
import config
from utils.logger import get_logger

logger = get_logger(__name__)

def take_screenshot():
    """Take a screenshot and save it to the screenshots directory."""
    # Create screenshots directory if it doesn't exist
    os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
    
    # Generate a filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    png_filename = f"screenshot_{timestamp}.png"
    png_path = os.path.join(config.SCREENSHOT_DIR, png_filename)
    
    # Take the screenshot
    screenshot = pyautogui.screenshot()
    screenshot.save(png_path, compress_level=9, optimize=True)
    
    if os.path.getsize(png_path) <= 5 * 1024 * 1024:
        return png_path
    
    jpg_filename = f"screenshot_{timestamp}.jpg"
    jpg_path = os.path.join(config.SCREENSHOT_DIR, jpg_filename)
    quality = 95
    while quality >= 10:
        screenshot.save(jpg_path, format='JPEG', quality=quality, optimize=True)
        if os.path.getsize(jpg_path) <= 5 * 1024 * 1024:
            os.remove(png_path)
            return jpg_path
        os.remove(jpg_path)
        quality -= 5

    logger.warning("Fail to compress screen shot under 5MB")
    return png_path
