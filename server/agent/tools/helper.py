import re
import requests
import json

def get_location_id(input:str)->str:
    pattern = r'location[^\d]*?(\d{9})'
    match = re.search(pattern, input)
    if match:
        location = match.group(1)
    else:
        location = "101010100"
    return location

def get_lon_lat(input:str)->str:
    pattern = ""
    return "116.38,39.91"

def get_date(input:str)->str:
    pattern = r'date[^\d]*?(\d{8})'
    match = re.search(pattern, input)
    if match:
        date = match.group(1)
    else:
        date = "20240530"
    return date

def parse_response(query: str, response: str):
    url = "https://api.openai-sb.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sb-e4ee00f210a9c5b787ea42831d8c472c3c52c9149d764ed1",
        "Content-Type": "application/json"
    }

    prompt = f"您好，我有一个需求：{query}。为此我调用了有关的API，API调用结果为:{response}，请你根据调用结果来回答我的问题、满足我的需求。"
    data = {
        "model": "gpt-3.5-turbo",
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(response)

    return response.json()['choices'][0]['message']['content']