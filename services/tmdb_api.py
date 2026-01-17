import aiohttp
from bot.config import settings
from bot.logger import logger

TMDB_BASE_URL = "https://api.themoviedb.org/3"

async def search_content(query: str, adult_user: bool):
    async with aiohttp.ClientSession() as session:
        url = f"{TMDB_BASE_URL}/search/multi"

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
            logger.debug(f"search_content({query}) called")
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
            logger.debug(f"get_movie_details({id}) called")
            return await response.json()
        
async def get_series_details(id: int):
    async with aiohttp.ClientSession() as session:
        url = f"{TMDB_BASE_URL}/tv/{id}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.TMDB_APIKEY}"
        }

        params = {
            "language": "en-US"
        }

        async with session.get(url, headers=headers, params=params) as response:
            logger.debug(f"get_series_details({id}) called")
            return await response.json()
        
async def get_similar_movie(id: int):
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
            logger.debug(f"get_similar_movie({id}) called")
            data = await response.json()
            return data.get("results", [])
        
async def get_similar_series(id: int):
    async with aiohttp.ClientSession() as session:
        url = f"{TMDB_BASE_URL}/tv/{id}/similar"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.TMDB_APIKEY}"
        }

        params = {
            "language": "en-US"
        }

        async with session.get(url, headers=headers, params=params) as response:
            logger.debug(f"get_similar_series({id}) called")
            data = await response.json()
            return data.get("results", [])