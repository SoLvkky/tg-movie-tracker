from aiogram import F, types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.keyboards.back_button import back_button
from bot.logger import logger
from database.crud import *
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.callback_query(F.data == "settings")
async def settings_menu(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()

    logger.info(f"User {callback.message.chat.id} used /settings")

    if(await get_adult(session=session, telegram_id=callback.message.chat.id)):\
        text_adult="✅ Adult - Show/Hide 18+ content"
    else:
        text_adult="❌ Adult - Show/Hide 18+ content"

    builder = InlineKeyboardBuilder()

    builder.button(text="Adult Mode", callback_data="adult")
    builder.attach(back_button("menu"))
    
    await callback.message.edit_text(
        text=f"Set your preferences:\n\n{text_adult}",
        reply_markup=builder.as_markup(),
    )

    logger.info(f"User @{callback.message.chat.username} used /settings command")

@router.callback_query(F.data == "adult")
async def adult_switch(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()

    adult_user = await toggle_adult(session=session, telegram_id=callback.message.chat.id)

    logger.info(f"User {callback.message.chat.id} toggled adult mode to {adult_user}")

    text_adult = "✅ Adult - Show/Hide 18+ content" if adult_user else "❌ Adult - Show/Hide 18+ content"

    builder = InlineKeyboardBuilder()

    builder.button(text="Adult Mode", callback_data="adult")
    builder.attach(back_button("menu"))
    
    await callback.message.edit_text(
        text=f"Set your preferences:\n\n{text_adult}",
        reply_markup=builder.as_markup(),
    )

    logger.info(f"User @{callback.message.chat.username} changed his Adult Mode to {adult_user}")