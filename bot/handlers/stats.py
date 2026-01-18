from aiogram import F,Router, types
from bot.keyboards.back_button import back_button
from bot.logger import logger
from database.crud import *
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.callback_query(F.data == "stats")
async def user_stats(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()

    user = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
    count = await get_user_movie_count(session=session, user_id=user.id)
    genres_list = await get_top_genres(session=session, user_id=user.id)
    genres = {row.genre: row.count for row in genres_list[:3]}

    builder = back_button("menu")

    logger.info(f"User @{callback.from_user.username} used /stats")

    await callback.message.edit_text(text=(
        f"👤 User: {callback.message.chat.username}\n\n"
        f"🎬 Movies watched: {count.get("movies")}\n"
        f"📺 TV Series watched: {count.get("series")}\n\n"
        f"🎭 Favorite genres:\n{'\n'.join(f"{genre}: {count}" for genre, count in genres.items())}\n"
    ), reply_markup=builder.as_markup())