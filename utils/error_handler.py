import traceback
from utils.logger import get_logger

logger = get_logger(__name__)

class AutomationError(Exception):
    """Base exception for automation errors."""
    def __init__(self, message, details=None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class APIError(AutomationError):
    """Exception raised for API-related errors."""
    pass

class VisionError(AutomationError):
    """Exception raised for vision analysis errors."""
    pass

class OperationError(AutomationError):
    """Exception raised for operation execution errors."""
    pass

def handle_error(func):
    """Decorator to handle exceptions in functions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AutomationError as e:
            logger.error(f"{e.__class__.__name__}: {e.message}")
            if e.details:
                logger.error(f"Details: {e.details}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            raise AutomationError(f"Unexpected error: {str(e)}", traceback.format_exc())
    return wrapper
