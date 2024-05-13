import json
import asyncio
from pydantic import BaseModel, Field
import aiohttp

async def get_currency():
    url = "https://booking-com15.p.rapidapi.com/api/v1/meta/getCurrency"
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()  # Return the parsed JSON data
            else:
                return {"error": f"Failed to fetch currency data, status code: {response.status}"}

def fetch_currency():
    return asyncio.run(get_currency())

class CurrencyInput(BaseModel):
    # This class is provided as an example if future implementations require input parameters
    pass

if __name__ == "__main__":
    result = fetch_currency()
    print("Answer:", result)
