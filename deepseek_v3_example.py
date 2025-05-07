import requests

url = "https://api.siliconflow.cn/v1/chat/completions"

payload = {
    "model": "deepseek-ai/DeepSeek-V3",
    "stream": False,
    "max_tokens": 512,
    "enable_thinking": True,
    "thinking_budget": 512,
    "min_p": 0.05,
    "temperature": 0.7,
    "top_p": 0.7,
    "top_k": 50,
    "frequency_penalty": 0.5,
    "n": 1,
    "stop": [],
    "messages": [
        {
            "role": "user",
            "content": "How are you today"
        }
    ]
}


SK_TOKEN="sk-123456789"
headers = {
    "Authorization": f"Bearer {SK_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)