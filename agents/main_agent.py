import json
import re
from agents.base_agent import BaseAgent
from agents.vision_agent import VisionAgent
from agents.operation_agent import OperationAgent
from executor.command_executor import CommandExecutor
from system.screenshot import take_screenshot
from system.state_manager import StateManager
from utils.logger import get_logger
from utils.error_handler import handle_error, AutomationError
import config

logger = get_logger(__name__)

class MainAgent(BaseAgent):
    def __init__(self):
        super().__init__(config.MAIN_AGENT_MODEL)
        self.vision_agent = VisionAgent()
        self.operation_agent = OperationAgent()
        self.command_executor = CommandExecutor()
        self.state_manager = StateManager()
    
    @handle_error
    def process(self, intent):
        """Process the user's intent."""
        plan = self._create_plan(intent)
        return self._execute_plan(plan)
    
    @handle_error
    async def process_intent(self, intent, task_id, session_id):
        """Process the user's intent and coordinate the automation."""
        
        logger.debug("Invoked MainAgent.process_intent")
        try:
            # Update task status
            self.state_manager.update_task_status(
                task_id, "planning", "Creating automation plan"
            )
            
            # Generate plan
            plan = self._create_plan(intent)
            logger.info(f"Created plan with {len(plan)} steps")
            
            # Execute each step in the plan
            for step_idx, step in enumerate(plan):
                # Update status
                self.state_manager.update_task_status(
                    task_id, "executing", f"Executing step {step_idx+1}/{len(plan)}: {step['description']}"
                )
                
                # Execute the step based on its type
                if step["type"] == "screenshot":
                    screenshot_path = take_screenshot()
                    self.state_manager.set_task_data(task_id, "last_screenshot", screenshot_path)
                    logger.info(f"Took screenshot: {screenshot_path}")
                
                elif step["type"] == "vision_analysis":
                    screenshot_path = self.state_manager.get_task_data(task_id, "last_screenshot")
                    if not screenshot_path:
                        # Take a screenshot if we don't have one
                        screenshot_path = take_screenshot()
                        self.state_manager.set_task_data(task_id, "last_screenshot", screenshot_path)
                    
                    element_data = self.vision_agent.analyze_screenshot(
                        screenshot_path, step["prompt"]
                    )
                    self.state_manager.set_task_data(task_id, "element_data", element_data)
                    logger.info(f"Vision analysis complete: {element_data}")
                
                elif step["type"] == "operation":
                    element_data = self.state_manager.get_task_data(task_id, "element_data")
                    operation_commands = self.operation_agent.generate_commands(
                        step["instruction"], element_data
                    )
                    
                    # Execute each command
                    for cmd in operation_commands:
                        logger.info(f"Executing command: {cmd}")
                        self.command_executor.execute(cmd)
            
            # Update task status to completed
            self.state_manager.update_task_status(
                task_id, "completed", "Automation task completed successfully"
            )
            
        except Exception as e:
            # Update task status to failed
            error_message = str(e)
            logger.error(f"Automation failed: {error_message}")
            self.state_manager.update_task_status(
                task_id, "failed", f"Automation failed: {error_message}"
            )
    
    @handle_error
    def _create_plan(self, intent):
        """Create a step-by-step plan based on the user's intent."""
        logger.info(f"Creating plan for intent: {intent}")
        
        messages = [
            {
                "role": "system",
                "content": """You are an AI automation planner. Your job is to create a detailed step-by-step plan to accomplish a user's intent using computer automation.
                Each step should be one of these types:
                1. 'screenshot' - Take a screenshot of the current screen
                2. 'vision_analysis' - Analyze the screenshot to find UI elements
                3. 'operation' - Perform a mouse or keyboard operation
                
                For each step, provide:
                - 'type': The step type
                - 'description': A brief description of the step
                - 'prompt' (for vision_analysis): The prompt to send to the vision model
                - 'instruction' (for operation): The instruction for the operation agent
                
                Return the plan as a JSON array of steps."""
            },
            {
                "role": "user",
                "content": f"Create a plan to accomplish this intent: {intent}"
            }
        ]
        
        response = self.call_api(messages)
        plan_text = response["choices"][0]["message"]["content"]
        logger.debug(f"Plan response: {plan_text}")
        
        # Extract JSON from the response
        try:
            # Find JSON in the response (it might be wrapped in markdown code blocks)
            json_match = re.search(r'```json\n(.*?)\n```', plan_text, re.DOTALL)
            if json_match:
                plan_json = json_match.group(1)
            else:
                plan_json = plan_text
                
            plan = json.loads(plan_json)
            
            # Validate the plan
            if not isinstance(plan, list):
                raise AutomationError("Expected a list of steps, got something else", plan_json)
            
            for step in plan:
                if not isinstance(step, dict):
                    raise AutomationError(f"Expected a step object, got {type(step)}", step)
                
                if "type" not in step:
                    raise AutomationError("Step missing 'type' field", step)
                
                if step["type"] not in ["screenshot", "vision_analysis", "operation"]:
                    raise AutomationError(f"Invalid step type: {step['type']}", step)
                
                if "description" not in step:
                    raise AutomationError("Step missing 'description' field", step)
                
                if step["type"] == "vision_analysis" and "prompt" not in step:
                    raise AutomationError("Vision analysis step missing 'prompt' field", step)
                
                if step["type"] == "operation" and "instruction" not in step:
                    raise AutomationError("Operation step missing 'instruction' field", step)
            
            return plan
            
        except json.JSONDecodeError:
            # If JSON parsing fails, create a simple default plan
            logger.warning("Failed to parse plan JSON, using default plan")
            return [
                {
                    "type": "screenshot",
                    "description": "Take a screenshot of the current screen"
                },
                {
                    "type": "vision_analysis",
                    "description": "Identify the target element",
                    "prompt": f"Find the element needed to accomplish: {intent}"
                },
                {
                    "type": "operation",
                    "description": "Perform the required operation",
                    "instruction": f"Execute operations to accomplish: {intent}"
                }
            ]
    
    @handle_error
    def _execute_plan(self, plan):
        """Execute a plan and return the results."""
        results = []
        
        for step_idx, step in enumerate(plan):
            logger.info(f"Executing step {step_idx+1}/{len(plan)}: {step['description']}")
            
            result = {"step": step_idx + 1, "description": step["description"], "status": "success"}
            
            try:
                if step["type"] == "screenshot":
                    screenshot_path = take_screenshot()
                    result["screenshot_path"] = screenshot_path
                
                elif step["type"] == "vision_analysis":
                    screenshot_path = results[-1].get("screenshot_path") if results else take_screenshot()
                    element_data = self.vision_agent.analyze_screenshot(
                        screenshot_path, step["prompt"]
                    )
                    result["element_data"] = element_data
                
                elif step["type"] == "operation":
                    element_data = next((r.get("element_data") for r in reversed(results) if "element_data" in r), None)
                    operation_commands = self.operation_agent.generate_commands(
                        step["instruction"], element_data
                    )
                    
                    # Execute each command
                    executed_commands = []
                    for cmd in operation_commands:
                        self.command_executor.execute(cmd)
                        executed_commands.append(cmd)
                    
                    result["executed_commands"] = executed_commands
                
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
                logger.error(f"Step {step_idx+1} failed: {str(e)}")
            
            results.append(result)
        
        return results
