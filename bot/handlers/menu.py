from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.keyboards.main_menu import get_main_menu
from bot.logger import logger

router = Router()

@router.message(Command("menu"))
async def cmd_start(message: Message) -> None:
    logger.info(f"User @{message.chat.username} used /menu command")
    await message.answer(text="Choose your option", reply_markup=get_main_menu())