import requests
import base64

url = "https://api.siliconflow.cn/v1/chat/completions"

path = "/Users/xuehaonan/Downloads/daspic.png"

with open(path, 'rb') as f:
    data = f.read()

base64_image = base64.b64encode(data).decode('utf-8')
image_data_url = f"data:image/png;base64,{base64_image}"

payload = {
    "model": "deepseek-ai/deepseek-vl2",
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
            "content": [
                {
                    "text": "<image>\n<|ref|>The woman with yellow clothes<|/ref|>.",
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
}

SK_TOKEN="sk-123456789"
headers = {
    "Authorization": f"Bearer {SK_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)

# Example return
"""
{
    "id":"0196ab7345ee0e77a182b5c8d95eeaa7",
    "object":"chat.completion",
    "created":1746633181,
    "model":"deepseek-ai/deepseek-vl2",
    "choices":[
        {
            "index":0,
            "message":{
                "role":"assistant",
                "content":"\u003c|ref|\u003eThe woman with yellow clothes\u003c|/ref|\u003e\u003c|det|\u003e[[371, 506, 428, 731]]\u003c|/det|\u003e"
            },
                "finish_reason":"stop"
        }],
    "usage":{
        "prompt_tokens":1822,
        "completion_tokens":21,
        "total_tokens":1843
    },
    "system_fingerprint":""
}
"""