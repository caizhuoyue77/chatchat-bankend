import json
import asyncio
from pydantic import BaseModel, Field
import aiohttp

async def get_exchange_rates(base_currency: str):
    url = "https://booking-com15.p.rapidapi.com/api/v1/meta/getExchangeRates"
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }
    params = {"base_currency": base_currency}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()  # Return the parsed JSON data
            else:
                return {"error": f"Failed to fetch exchange rates, status code: {response.status}"}

def fetch_exchange_rates(base_currency: str):
    return asyncio.run(get_exchange_rates(base_currency))

class ExchangeRatesInput(BaseModel):
    base_currency: str = Field(description="Base currency code to retrieve exchange rates for")

if __name__ == "__main__":
    base_currency = "USD"
    result = fetch_exchange_rates(base_currency)
    print("Answer:", result)