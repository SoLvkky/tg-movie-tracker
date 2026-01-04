from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.states.movie_states import MovieStates
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
async def go_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(
        text="Choose your option:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "my_movies")
async def get_movies(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
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