from aiogram import types, Router
from aiogram.filters import Command
from bot.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from database.crud import get_or_create_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, session: AsyncSession):
    user = await get_or_create_user(session=session, telegram_id=message.chat.id, username=message.chat.username)

    logger.info(f"User @{message.chat.username} used /start command")

    await message.answer(
        "Hi! I'll help you keep track of the movies you've watched\n\n"
        "Commands:\n"
        "/menu - Main Menu"
    )