import aiohttp
from bot.config import settings

TMDB_BASE_URL = "https://api.themoviedb.org/3"

async def search_movie(query: str, adult_user: bool):
    async with aiohttp.ClientSession() as session:
        url = f"{TMDB_BASE_URL}/search/movie"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.TMDB_APIKEY}"
        }

        params = {
            "include_adult": "true" if adult_user else "false",
            "language": "en-US",
            "query": query
        }

        async with session.get(url, headers=headers, params=params) as response:
            data = await response.json()
            return data.get("results", [])
        
async def get_movie_details(id: int):
    async with aiohttp.ClientSession() as session:
        url = f"{TMDB_BASE_URL}/movie/{id}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.TMDB_APIKEY}"
        }

        params = {
            "language": "en-US"
        }
        
        async with session.get(url, headers=headers, params=params) as response:
            return await response.json()
        
async def get_similar(id: int):
    async with aiohttp.ClientSession() as session:
        url = f"{TMDB_BASE_URL}/movie/{id}/similar"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.TMDB_APIKEY}"
        }

        params = {
            "language": "en-US"
        }

        async with session.get(url, headers=headers, params=params) as response:
            data = await response.json()
            return data.get("results", [])