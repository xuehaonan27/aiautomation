import requests
import json
from abc import ABC, abstractmethod
import config

class BaseAgent(ABC):
    def __init__(self, model_name):
        self.api_url = config.DEEPSEEK_API_URL
        self.api_key = config.DEEPSEEK_API_KEY
        self.model_name = model_name
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def call_api(self, messages, max_tokens=512, temperature=0.7):
        """Call the DeepSeek API with the given messages."""
        payload = {
            "model": self.model_name,
            "stream": False,
            "max_tokens": max_tokens,
            "enable_thinking": True,
            "thinking_budget": 512,
            "min_p": 0.05,
            "temperature": temperature,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "stop": [],
            "messages": messages
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API call failed: {str(e)}")
    
    @abstractmethod
    def process(self, *args, **kwargs):
        """Process method to be implemented by each agent."""
        pass
