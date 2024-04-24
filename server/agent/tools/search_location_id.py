import json
import asyncio
from pydantic import BaseModel, Field
import requests

async def search_location_id(location: str):
    base_url = "http://162.105.88.82:57861//api/get_location_id"


    params = {
        "location": location
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
    return asyncio.run(search_location_id(location))

class LocationInput(BaseModel):
    location: str = Field(description="地点的名称，比如beijing或者changsha")