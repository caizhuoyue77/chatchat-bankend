import json
import asyncio
from pydantic import BaseModel, Field
import requests

async def search_current_weather_iter(location: str):
    base_url = "http://162.105.88.82:57861//api/get_current_weather"

    import re

    pattern = r"\d+"
    matches = re.findall(pattern, location)

    print(matches[0])

    params = {
        "location": "101040100"
    }

    # 发送GET请求
    try:
        response = requests.get(base_url, params=params)

        # 检查响应状态码
        if response.status_code == 200:
            return response.json()  # 返回解析后的JSON数据
        else:
            return {"error": f"Failed to fetch weather information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def search_current_weather(location: str):
    return asyncio.run(search_current_weather_iter(location))

class WeatherInput(BaseModel):
    location: str = Field(description="地点的ID")