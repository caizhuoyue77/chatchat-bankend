import json
import asyncio
from pydantic import BaseModel, Field
import requests

async def search_express_iter(tracking_no: str):
    base_url = "http://162.105.88.82:57861/other/get_express_info"
    params = {
        "tracking_no": tracking_no
    }

    # 发送GET请求
    try:
        response = requests.get(base_url, params=params)

        # 检查响应状态码
        if response.status_code == 200:
            return response.json()  # 返回解析后的JSON数据
        else:
            return {"error": f"Failed to fetch express information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def search_express(tracking_no: str):
    return asyncio.run(search_express_iter(tracking_no))

class ExpressInput(BaseModel):
    tracking_no: str = Field(description="物流单号")

if __name__ == "__main__":
    result = search_express("YT7457241805741")
    print("答案:",result)
