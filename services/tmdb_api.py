import aiohttp
from bot.config import settings
from bot.logger import logger

TMDB_BASE_URL = "https://api.themoviedb.org/3"

async def search_content(query: str, adult_user: bool, lang: str = "en-US"):
    async with aiohttp.ClientSession() as session:
        url = f"{TMDB_BASE_URL}/search/multi"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.TMDB_APIKEY}"
        }

        params = {
            "include_adult": "true" if adult_user else "false",
            "language": lang,
            "query": query
        }

        async with session.get(url, headers=headers, params=params) as response:
            logger.debug(f"search_content({query}) called")
            data = await response.json()
            return data.get("results", [])

async def get_content(content_type: str, id: int, lang: str = "en-US", method: str = ""):
    async with aiohttp.ClientSession() as session:
        url = f"{TMDB_BASE_URL}/{content_type}/{id}{method}"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.TMDB_APIKEY}"
        }

        params = {
            "language": lang
        }
        
        async with session.get(url, params=params, headers=headers) as response:
            logger.debug(f"get_content({id}) called")
            data = await response.json()
            match method:
                case "":
                    return data
                case _:
                    return data.get("results")    
        
async def get_trending(trending_type: str, lang: str = "en-US"):
    async with aiohttp.ClientSession() as session:
        url = f"{TMDB_BASE_URL}/trending/{trending_type}/week"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.TMDB_APIKEY}"
        }

        params = {
            "language": lang
        }

        async with session.get(url, headers=headers, params=params) as response:
            logger.debug(f"get_trending_series({trending_type}) called")
            data = await response.json()
            return data.get("results")