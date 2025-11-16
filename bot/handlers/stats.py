from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.keyboards.main_menu import get_main_menu
from bot.logger import logger
from database.crud import *
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

def back_button(callback_data: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="GO BACK", callback_data=callback_data)
    builder.adjust(1)

    return builder

@router.callback_query(lambda c: c.data == "menu")
async def go_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="Choose your option:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "stats")
async def user_stats(callback: types.CallbackQuery, session: AsyncSession):
    user = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
    count = await get_user_movie_count(session=session, user_id=user.id)
    genres_list = await get_top_genres(session=session, user_id=user.id)
    genres = {row.genre: row.count for row in genres_list[:3]}

    builder = back_button("menu")

    logger.info(f"User @{callback.from_user.username} used /stats command")

    await callback.message.edit_text(text=(
        f"👤 User: {callback.message.chat.username}\n\n"
        f"🎬 Movies watched: {count}\n\n"
        f"🎭 Favorite genres:\n{'\n'.join(f"{genre}: {count} movies" for genre, count in genres.items())}\n"
    ), reply_markup=builder.as_markup())