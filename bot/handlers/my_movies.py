from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.states.movie_states import MovieStates
from bot.keyboards.back_button import back_button
from bot.logger import logger
from database.crud import *
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.callback_query(F.data == "my_movies")
async def get_movies(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()

    user = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
    movies = await get_watched_movies(session=session, user_id=user.id)

    logger.info(f"User @{callback.from_user.username} used /my-movies command")

    if movies:
        builder = InlineKeyboardBuilder()

        for m in movies:
            builder.button(text=f'{m["title"]}, {m["year"]}', callback_data=str(m["tmdb_id"]))

        builder.attach(back_button("menu"))

        await callback.message.edit_text(text="Your movies:", reply_markup=builder.as_markup())

        await state.set_state(MovieStates.waiting_for_choice)
        await state.update_data(parent="my_movies")

    else:
        builder = back_button("menu")

        await callback.message.edit_text(text="You have no movies!", reply_markup=builder.as_markup())