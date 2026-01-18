import asyncio
from aiogram import F, Router, types, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards.main_menu import get_main_menu
from bot.logger import logger

router = Router()

@router.message(Command("menu"))
async def cmd_start(message: Message) -> None:
    logger.info(f"User @{message.chat.username} used /menu")
    await message.answer(text="Choose your option:", reply_markup=get_main_menu())

@router.callback_query(F.data == "menu")
async def go_to_menu(callback: types.CallbackQuery):
    await callback.answer()

    logger.info(f"User @{callback.message.chat.username} used /menu")

    await callback.message.edit_text(
        text="Choose your option:",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "menu_delete")
async def delete_menu(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    await state.clear()

    logger.info(f"User @{callback.message.chat.username} used /menu")

    send_task = bot(callback.message.answer(
        text="Choose your option:",
        reply_markup=get_main_menu()
    ))
    del_task = bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id
    )

    await asyncio.gather(send_task, del_task)