from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid

from agents.main_agent import MainAgent
from system.state_manager import StateManager

router = APIRouter()
state_manager = StateManager()

class IntentRequest(BaseModel):
    intent: str
    session_id: Optional[str] = None

class AutomationResponse(BaseModel):
    task_id: str
    status: str
    message: str

@router.post("/automate", response_model=AutomationResponse)
async def automate(request: IntentRequest, background_tasks: BackgroundTasks):
    # Generate a unique task ID
    task_id = str(uuid.uuid4())
    
    # Create a session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Initialize the main agent
    main_agent = MainAgent()
    
    # Register the task in the state manager
    state_manager.register_task(task_id, session_id)
    
    # Process the intent in the background
    background_tasks.add_task(
        main_agent.process_intent,
        intent=request.intent,
        task_id=task_id,
        session_id=session_id
    )
    
    return AutomationResponse(
        task_id=task_id,
        status="processing",
        message="Automation task started"
    )

@router.get("/status/{task_id}", response_model=AutomationResponse)
async def get_status(task_id: str):
    status = state_manager.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return AutomationResponse(
        task_id=task_id,
        status=status["status"],
        message=status["message"]
    )
