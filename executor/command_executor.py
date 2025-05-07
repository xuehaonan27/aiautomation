import re
import time
import pyautogui
from utils.logger import get_logger
from utils.error_handler import handle_error, OperationError

logger = get_logger(__name__)

class CommandExecutor:
    def __init__(self):
        # Configure pyautogui
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        
    @handle_error
    def execute(self, command_str):
        """Execute a standardized command using pyautogui."""
        logger.info(f"Executing command: {command_str}")
        
        # Parse the command and arguments
        match = re.match(r'(\w+)\((.*)\)', command_str)
        if not match:
            raise OperationError(f"Invalid command format: {command_str}")
        
        command, args_str = match.groups()
        
        # Parse arguments
        args = []
        kwargs = {}
        
        if args_str:
            # Handle string arguments with commas inside quotes
            in_quotes = False
            current_arg = ""
            arg_list = []
            
            for char in args_str:
                if char == '"' or char == "'":
                    in_quotes = not in_quotes
                    current_arg += char
                elif char == ',' and not in_quotes:
                    arg_list.append(current_arg.strip())
                    current_arg = ""
                else:
                    current_arg += char
            
            if current_arg:
                arg_list.append(current_arg.strip())
            
            # Evaluate each argument
            for arg in arg_list:
                try:
                    # Handle keyword arguments
                    if '=' in arg and not (arg.startswith('"') or arg.startswith("'")):
                        key, val = arg.split('=', 1)
                        kwargs[key.strip()] = eval(val.strip())
                    else:
                        # Handle positional arguments
                        args.append(eval(arg))
                except:
                    # If eval fails, treat as string without quotes
                    if arg.startswith('"') or arg.startswith("'"):
                        args.append(eval(arg))
                    else:
                        args.append(arg)
        
        # Execute the command
        try:
            if command == "mouse_move":
                x, y = args
                pyautogui.moveTo(x, y, duration=0.5)
            
            elif command == "mouse_left_click":
                if args:
                    x, y = args
                    pyautogui.click(x, y)
                else:
                    pyautogui.click()
            
            elif command == "mouse_right_click":
                if args:
                    x, y = args
                    pyautogui.rightClick(x, y)
                else:
                    pyautogui.rightClick()
            
            elif command == "mouse_double_click":
                if args:
                    x, y = args
                    pyautogui.doubleClick(x, y)
                else:
                    pyautogui.doubleClick()
            
            elif command == "keyboard_type":
                text = args[0]
                pyautogui.typewrite(text)
            
            elif command == "keyboard_press":
                key = args[0]
                pyautogui.press(key)
            
            elif command == "keyboard_hotkey":
                pyautogui.hotkey(*args)
            
            elif command == "wait":
                seconds = args[0]
                time.sleep(seconds)
            
            else:
                raise OperationError(f"Unknown command: {command}")
            
            # Small delay between commands for stability
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            raise OperationError(f"Failed to execute command '{command_str}': {str(e)}")
