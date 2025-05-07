import threading
from datetime import datetime

class StateManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StateManager, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        self.tasks = {}
        self.sessions = {}
    
    def register_task(self, task_id, session_id):
        """Register a new task."""
        with self._lock:
            self.tasks[task_id] = {
                "session_id": session_id,
                "status": "created",
                "message": "Task created",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "data": {}
            }
            
            # Add task to session
            if session_id not in self.sessions:
                self.sessions[session_id] = []
            self.sessions[session_id].append(task_id)
    
    def update_task_status(self, task_id, status, message):
        """Update the status of a task."""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = status
                self.tasks[task_id]["message"] = message
                self.tasks[task_id]["updated_at"] = datetime.now()
    
    def get_task_status(self, task_id):
        """Get the status of a task."""
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                return {
                    "status": task["status"],
                    "message": task["message"],
                    "created_at": task["created_at"],
                    "updated_at": task["updated_at"]
                }
            return None
    
    def set_task_data(self, task_id, key, value):
        """Set data for a task."""
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id]["data"][key] = value
    
    def get_task_data(self, task_id, key, default=None):
        """Get data for a task."""
        with self._lock:
            if task_id in self.tasks and key in self.tasks[task_id]["data"]:
                return self.tasks[task_id]["data"][key]
            return default
    
    def get_session_tasks(self, session_id):
        """Get all tasks for a session."""
        with self._lock:
            if session_id in self.sessions:
                return self.sessions[session_id]
            return []
