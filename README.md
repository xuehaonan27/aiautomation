# AI Automation System

A multi-agent system for automating computer operations using AI. This system uses DeepSeek's language and vision models to control the computer through mouse and keyboard operations.

## Architecture

The system consists of three main agents:

1. **Main Agent (Planner)** - Coordinates the automation process, creates plans, and manages the workflow.
2. **Vision Agent** - Analyzes screenshots to identify UI elements and their positions.
3. **Operation Agent** - Generates specific automation commands based on high-level instructions.

## Features

- HTTP service for receiving automation intents via curl
- Screenshot capture and analysis
- Mouse and keyboard automation via pyautogui
- Task state management and status tracking
- Error handling and recovery

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aiautomation.git
   cd aiautomation
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file to add your DeepSeek API key and other configuration options.

## Usage

1. Start the service:
   ```bash
   python main.py
   ```

2. Send automation requests:
   ```bash
   curl -X POST http://localhost:8000/automate \
     -H "Content-Type: application/json" \
     -d '{"intent": "帮我在输入框中输入'你好'."}'
   ```

3. Check task status:
   ```bash
   curl http://localhost:8000/status/{task_id}
   ```

## Example Workflow

For the intent "帮我在输入框中输入'你好'":

1. Main Agent creates a plan:
   - Take a screenshot
   - Identify input field location
   - Move cursor to input field
   - Click on input field
   - Type "你好"

2. Vision Agent analyzes the screenshot to find the input field
3. Operation Agent generates commands to move the mouse and type text
4. Command Executor performs the operations using pyautogui

## Project Structure

```
aiautomation/
├── main.py                  # Entry point for the application
├── config.py                # Configuration settings
├── service/                 # HTTP service implementation
├── agents/                  # AI agents implementation
├── executor/                # Command execution
├── system/                  # System utilities
└── utils/                   # Helper utilities
```

## Requirements

- Python 3.8+
- FastAPI
- PyAutoGUI
- Requests
- Python-dotenv

## License

MIT
