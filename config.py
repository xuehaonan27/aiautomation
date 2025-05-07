import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))

# Model Configuration
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.siliconflow.cn/v1/chat/completions')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-123456789')  # Replace with actual key in .env

# Agent Configuration
MAIN_AGENT_MODEL = os.getenv('MAIN_AGENT_MODEL', 'deepseek-ai/DeepSeek-V3')
VISION_AGENT_MODEL = os.getenv('VISION_AGENT_MODEL', 'deepseek-ai/deepseek-vl2')
OPERATION_AGENT_MODEL = os.getenv('OPERATION_AGENT_MODEL', 'deepseek-ai/DeepSeek-V3')

# System Configuration
SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR', './screenshots')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
