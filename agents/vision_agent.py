import base64
from agents.base_agent import BaseAgent
from utils.logger import get_logger
from utils.error_handler import handle_error, VisionError
import config
import re

logger = get_logger(__name__)

class VisionAgent(BaseAgent):
    def __init__(self):
        super().__init__(config.VISION_AGENT_MODEL)
    
    @handle_error
    def process(self, screenshot_path, prompt):
        """Process a screenshot with a prompt."""
        return self.analyze_screenshot(screenshot_path, prompt)
    
    @handle_error
    def analyze_screenshot(self, screenshot_path, prompt):
        """Analyze a screenshot to identify UI elements."""
        logger.info(f"Analyzing screenshot: {screenshot_path}")
        logger.info(f"Prompt: {prompt}")
        
        # Read and encode the screenshot
        try:
            with open(screenshot_path, 'rb') as f:
                image_data = f.read()
        except Exception as e:
            raise VisionError(f"Failed to read screenshot: {str(e)}")
        
        base64_image = base64.b64encode(image_data).decode('utf-8')
        image_data_url = f"data:image/png;base64,{base64_image}"
        
        # Prepare the message with the reference prompt
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "text": f"<image>\n<|ref|>{prompt}<|/ref|>.",
                        "type": "text"
                    },
                    {
                        "image_url": {
                            "detail": "auto",
                            "url": image_data_url,
                        },
                        "type": "image_url"
                    }
                ]
            }
        ]
        
        # Call the vision API
        try:
            response = self.call_api(messages)
            
            # Parse the response to extract element coordinates
            content = response["choices"][0]["message"]["content"]
            logger.debug(f"Vision API response: {content}")
            
            # Extract coordinates from the response
            # Format: <|ref|>prompt<|/ref|><|det|>[[x1, y1, x2, y2]]<|/det|>
            coords_match = re.search(r'<\|det\|>(.*?)<\|/det\|>', content)
            
            if coords_match:
                try:
                    coords_str = coords_match.group(1)
                    # Parse the coordinates (format: [[x1, y1, x2, y2]])
                    import ast
                    coords = ast.literal_eval(coords_str)
                    
                    # Return the element data
                    result = {
                        "element_type": "ui_element",
                        "coordinates": coords,
                        "raw_response": content
                    }
                    
                    logger.info(f"Found element at coordinates: {coords}")
                    return result
                    
                except Exception as e:
                    raise VisionError(f"Failed to parse vision response: {str(e)}", content)
            else:
                raise VisionError("No element coordinates found in vision response", content)
                
        except Exception as e:
            if isinstance(e, VisionError):
                raise
            raise VisionError(f"Vision API call failed: {str(e)}")
