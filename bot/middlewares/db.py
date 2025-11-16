from aiogram import BaseMiddleware
from bot.logger import logger
from typing import Callable, Awaitable, Dict, Any
from sqlalchemy.ext.asyncio import async_sessionmaker

class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker):
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        logger.debug("Opening DB session")
        async with self.sessionmaker() as session:
            data["session"] = session
            try:
                response = await handler(event, data)
                return response

            except Exception as e:
                logger.error("Error inside DB middleware", exc_info=True)
                raise

            finally:
                logger.debug("Closing DB session")
        
