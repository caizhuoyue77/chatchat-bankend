import asyncio
import requests
from pydantic import BaseModel, Field

class IMDbTop100Input(BaseModel):
    query: str = Field(description="用于请求IMDb前100部电影的查询字符串。")

async def fetch_imdb_top_100_movies_iter() -> dict:
    """
    Asynchronously fetches the top 100 movies list from IMDb via the RapidAPI service.
    
    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://imdb-top-100-movies.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "imdb-top-100-movies.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch IMDb top 100 movies, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def fetch_imdb_top_100_movies() -> dict:
    """
    A synchronous wrapper function to fetch the IMDb top 100 movies.

    Returns:
        dict: The result from the asynchronous fetch function, containing either the top 100 movies or an error message.
    """
    return asyncio.run(fetch_imdb_top_100_movies_iter())

if __name__ == "__main__":
    movies_data = fetch_imdb_top_100_movies()
    print("IMDb Top 100 Movies:", movies_data)
