#!/usr/bin/env python3
"""
Test script for the AI Automation System.
This script tests the basic functionality of the system by sending a test intent.
"""

import requests
import json
import time
import sys
import os

# Default server URL
SERVER_URL = "http://localhost:8000"

def test_automation(intent):
    """Test the automation system with the given intent."""
    print(f"Testing automation with intent: '{intent}'")
    
    # Send the automation request
    try:
        response = requests.post(
            f"{SERVER_URL}/automate",
            json={"intent": intent}
        )
        response.raise_for_status()
        
        task_data = response.json()
        task_id = task_data["task_id"]
        
        print(f"Task created with ID: {task_id}")
        print(f"Initial status: {task_data['status']} - {task_data['message']}")
        
        # Poll for task status
        while True:
            time.sleep(2)  # Wait 2 seconds between polls
            
            status_response = requests.get(f"{SERVER_URL}/status/{task_id}")
            status_response.raise_for_status()
            
            status_data = status_response.json()
            print(f"Status: {status_data['status']} - {status_data['message']}")
            
            # Check if the task is completed or failed
            if status_data["status"] in ["completed", "failed"]:
                break
        
        # Print final result
        if status_data["status"] == "completed":
            print("\nAutomation completed successfully!")
        else:
            print("\nAutomation failed.")
            
        return status_data["status"] == "completed"
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Main function."""
    # Check if the server is running
    try:
        requests.get(f"{SERVER_URL}")
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to the server at {SERVER_URL}")
        print("Make sure the server is running by executing 'python main.py'")
        sys.exit(1)
    
    # Use the provided intent or a default one
    intent = sys.argv[1] if len(sys.argv) > 1 else "帮我在输入框中输入'你好'."
    
    # Run the test
    success = test_automation(intent)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
