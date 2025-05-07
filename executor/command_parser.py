import re
from utils.logger import get_logger
from utils.error_handler import handle_error, OperationError

logger = get_logger(__name__)

class CommandParser:
    """Parser for standardized automation commands."""
    
    @staticmethod
    @handle_error
    def parse_command(command_str):
        """
        Parse a command string into command name and arguments.
        
        Args:
            command_str (str): The command string to parse (e.g., "mouse_move(100, 200)")
            
        Returns:
            tuple: (command_name, args, kwargs) where:
                - command_name (str): The name of the command
                - args (list): Positional arguments
                - kwargs (dict): Keyword arguments
                
        Raises:
            OperationError: If the command format is invalid
        """
        # Match the command name and arguments
        match = re.match(r'(\w+)\((.*)\)', command_str)
        if not match:
            raise OperationError(f"Invalid command format: {command_str}")
        
        command_name, args_str = match.groups()
        
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
                        kwargs[key.strip()] = CommandParser._safe_eval(val.strip())
                    else:
                        # Handle positional arguments
                        args.append(CommandParser._safe_eval(arg))
                except Exception as e:
                    logger.warning(f"Error parsing argument '{arg}': {str(e)}")
                    # If eval fails, treat as string without quotes
                    if arg.startswith('"') or arg.startswith("'"):
                        try:
                            args.append(eval(arg))
                        except:
                            args.append(arg)
                    else:
                        args.append(arg)
        
        return command_name, args, kwargs
    
    @staticmethod
    def _safe_eval(expr):
        """
        Safely evaluate an expression.
        
        Args:
            expr (str): The expression to evaluate
            
        Returns:
            The evaluated expression
            
        Raises:
            ValueError: If the expression is not safe to evaluate
        """
        # Check if it's a simple number
        if re.match(r'^-?\d+(\.\d+)?$', expr):
            if '.' in expr:
                return float(expr)
            return int(expr)
        
        # Check if it's a string literal
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return eval(expr)
        
        # Check if it's a boolean
        if expr.lower() == 'true':
            return True
        if expr.lower() == 'false':
            return False
        
        # Check if it's None
        if expr.lower() == 'none':
            return None
        
        # For other expressions, use eval but be cautious
        try:
            result = eval(expr)
            return result
        except Exception as e:
            raise ValueError(f"Could not safely evaluate '{expr}': {str(e)}")
    
    @staticmethod
    def validate_command(command_name, args, kwargs):
        """
        Validate a command and its arguments.
        
        Args:
            command_name (str): The name of the command
            args (list): Positional arguments
            kwargs (dict): Keyword arguments
            
        Returns:
            bool: True if the command is valid
            
        Raises:
            OperationError: If the command is invalid
        """
        valid_commands = {
            "mouse_move": {"required_args": 2, "optional_args": 0},
            "mouse_left_click": {"required_args": 0, "optional_args": 2},
            "mouse_right_click": {"required_args": 0, "optional_args": 2},
            "mouse_double_click": {"required_args": 0, "optional_args": 2},
            "keyboard_type": {"required_args": 1, "optional_args": 0},
            "keyboard_press": {"required_args": 1, "optional_args": 0},
            "keyboard_hotkey": {"required_args": 1, "optional_args": 10},  # Allow multiple keys
            "wait": {"required_args": 1, "optional_args": 0},
        }
        
        if command_name not in valid_commands:
            raise OperationError(f"Unknown command: {command_name}")
        
        cmd_spec = valid_commands[command_name]
        min_args = cmd_spec["required_args"]
        max_args = min_args + cmd_spec["optional_args"]
        
        if len(args) < min_args:
            raise OperationError(f"Command '{command_name}' requires at least {min_args} arguments, got {len(args)}")
        
        if len(args) > max_args and max_args > 0:  # Only check if there's a limit
            raise OperationError(f"Command '{command_name}' accepts at most {max_args} arguments, got {len(args)}")
        
        return True
