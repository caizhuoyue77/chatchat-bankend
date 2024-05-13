import json
import asyncio
from pydantic import BaseModel, Field
import requests

async def search_hotel_iter(tracking_no: str):
    url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"

    querystring = {
        "dest_id":"-1924465",
        "search_type":"CITY",
        "arrival_date":"2024-05-15",
        "departure_date":"2024-05-17",
        "adults":"1",
        "children_age":"",
        "room_qty":"1",
        "page_number":"1",
        "languagecode":"zh-cn",
        "currency_code":"CNY"
        }

    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }

    try:
        return "北京的酒店有:1.w酒店 10000元 2.希尔顿酒店 800元 3.丽思卡尔顿酒店 2000元"
        
        # response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:

            
            json_str = json.dumps(response.json()["data"]["hotels"])

            return json_str[:2000]

            return response.json()
        else:
            return {"error": f"Failed to fetch hotel destination information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

    print(response.json())
    
def search_hotel(tracking_no: str):
    return asyncio.run(search_hotel_iter(tracking_no))

class HotelInput(BaseModel):
    tracking_no: str = Field(description="搜索信息")

if __name__ == "__main__":
    result = search_hotel("YT7457241805741")
    print("答案:",result)