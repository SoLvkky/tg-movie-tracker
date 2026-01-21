import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from bot.middlewares.db import DatabaseMiddleware
from bot.middlewares.i18n import I18nMiddleware
from bot.config import settings
from bot.handlers import content_handler, menu, my_collection, search, setting, start, stats, trending
from bot.logger import logger
from bot.i18n import load_locales

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
logger.info("✅ Config loaded")

dp = Dispatcher()

async def main():
    load_locales()
    logger.info("✅ Locales loaded")

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    logger.info("✅ Database engine created")

    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    dp.update.middleware(DatabaseMiddleware(sessionmaker))
    dp.update.middleware(I18nMiddleware())
    logger.info("✅ Middleware updated")

    dp.include_routers(
        start.router,
        menu.router,
        search.router,
        stats.router,
        my_collection.router,
        content_handler.router,
        setting.router,
        trending.router
    )
    logger.info("✅ Routers in DP registered")

    logger.info("✅ Bot has started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error("Bot crashed on startup", exc_info=True)
