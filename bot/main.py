import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from bot.middlewares.db import DatabaseMiddleware
from bot.config import settings
from bot.handlers import menu, setting, start, add_movie, stats, my_movies, movie_handler
from bot.logger import logger

async def main():
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    logger.info("Config loaded")

    dp = Dispatcher()

    dp.include_routers(
        start.router,
        menu.router,
        add_movie.router,
        stats.router,
        my_movies.router,
        movie_handler.router,
        setting.router,
    )
    logger.info("Routers in DP registered")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    logger.info("Database engine created")

    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    dp.update.middleware(DatabaseMiddleware(sessionmaker))
    logger.info("Middleware updated")

    logger.info("Bot has started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error("Bot crashed on startup", exc_info=True)
