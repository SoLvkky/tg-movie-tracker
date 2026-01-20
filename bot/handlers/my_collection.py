from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.states.search_states import SearchStates
from bot.keyboards.back_button import back_button
from bot.logger import logger
from bot.i18n import t
from database.crud import *
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.callback_query(F.data == "my_collection")
async def get_movies(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()

    user = await session.scalar(select(User).where(User.telegram_id == callback.message.chat.id))
    movies = await get_watched(session=session, user_id=user.id)

    logger.info(f"User @{callback.from_user.username} used /my-collection")

    if movies:
        builder = InlineKeyboardBuilder()

        for m in movies:
            media_type = await get_media_type(session, m["tmdb_id"])
            match media_type:
                case 1: callback_answer = "movie_choice"
                case 2: callback_answer = "tv_choice"
            builder.button(text=f'{m["title"]}, {m["year"]}', callback_data=str(f"{callback_answer}:{m['tmdb_id']}"))

        builder.attach(back_button("menu"))
        builder.adjust(1)

        await callback.message.edit_text(text=t("collection.text"), reply_markup=builder.as_markup())

        await state.set_state(SearchStates.waiting_for_choice)
        await state.update_data(parent="my_collection")

    else:
        builder = back_button("menu")

        await callback.message.edit_text(text=t("collection.empty"), reply_markup=builder.as_markup())