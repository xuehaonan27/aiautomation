import json
import re
from agents.base_agent import BaseAgent
from utils.logger import get_logger
from utils.error_handler import handle_error, OperationError
import config

logger = get_logger(__name__)

class OperationAgent(BaseAgent):
    def __init__(self):
        super().__init__(config.OPERATION_AGENT_MODEL)
    
    @handle_error
    def process(self, instruction, element_data=None):
        """Process an instruction and generate commands."""
        return self.generate_commands(instruction, element_data)
    
    @handle_error
    def generate_commands(self, instruction, element_data=None):
        """Generate standardized commands based on the instruction and element data."""
        logger.info(f"Generating commands for instruction: {instruction}")
        
        # Prepare the context with element data if available
        context = ""
        if element_data:
            coords = element_data["coordinates"]
            # For multiple elements, use the first one or process all as needed
            if isinstance(coords[0], list):
                x1, y1, x2, y2 = coords[0]
            else:
                x1, y1, x2, y2 = coords
                
            # Calculate center point
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            context = f"""
            Element information:
            - Type: {element_data.get('element_type', 'ui_element')}
            - Coordinates: [x1={x1}, y1={y1}, x2={x2}, y2={y2}]
            - Center point: [x={center_x}, y={center_y}]
            """
        
        # Prepare the message
        messages = [
            {
                "role": "system",
                "content": """You are an operation agent that generates standardized commands for computer automation.
                Generate a sequence of commands to accomplish the given instruction.
                
                Available commands:
                - mouse_move(x, y): Move the mouse to the specified coordinates
                - mouse_left_click(): Perform a left mouse click
                - mouse_right_click(): Perform a right mouse click
                - mouse_double_click(): Perform a double click
                - keyboard_type(text): Type the specified text
                - keyboard_press(key): Press a specific key (e.g., 'enter', 'tab', 'esc')
                - keyboard_hotkey(key1, key2, ...): Press a key combination (e.g., 'ctrl', 'c')
                - wait(seconds): Wait for the specified number of seconds
                
                Return the commands as a JSON array of strings."""
            },
            {
                "role": "user",
                "content": f"{context}\n\nInstruction: {instruction}"
            }
        ]
        
        # Call the API
        try:
            response = self.call_api(messages)
            commands_text = response["choices"][0]["message"]["content"]
            logger.debug(f"Operation agent response: {commands_text}")
            
            # Extract JSON from the response
            try:
                # Find JSON in the response (it might be wrapped in markdown code blocks)
                json_match = re.search(r'```json\n(.*?)\n```', commands_text, re.DOTALL)
                if json_match:
                    commands_json = json_match.group(1)
                else:
                    commands_json = commands_text
                    
                commands = json.loads(commands_json)
                
                # Validate that we got a list of strings
                if not isinstance(commands, list):
                    raise OperationError("Expected a list of commands, got something else", commands_json)
                
                # Validate each command
                for cmd in commands:
                    if not isinstance(cmd, str):
                        raise OperationError(f"Expected a string command, got {type(cmd)}", cmd)
                    
                    # Basic validation that it looks like a command
                    if not re.match(r'^\w+\(.*\)$', cmd):
                        raise OperationError(f"Invalid command format: {cmd}")
                
                logger.info(f"Generated {len(commands)} commands")
                return commands
                
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract commands line by line
                lines = commands_text.strip().split('\n')
                commands = []
                for line in lines:
                    # Remove common prefixes like "- ", numbers, etc.
                    clean_line = re.sub(r'^[\s\d\-\*\.]+', '', line).strip()
                    if clean_line and '(' in clean_line and ')' in clean_line:
                        commands.append(clean_line)
                
                if not commands:
                    raise OperationError("Failed to parse operation commands", commands_text)
                    
                logger.info(f"Extracted {len(commands)} commands from text response")
                return commands
                
        except Exception as e:
            if isinstance(e, OperationError):
                raise
            raise OperationError(f"Failed to generate commands: {str(e)}")
