import requests
import json

def call_openai(query:str):
    url = "https://api.openai-sb.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sb-e4ee00f",
        # 210a9c5b787ea42831d8c472c3c52c9149d764ed1
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()['choices'][0]['message']['content']

result = call_openai()
print(result)