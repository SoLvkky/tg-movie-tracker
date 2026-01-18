from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.states.search_states import SearchStates
from bot.keyboards.back_button import back_button
from bot.logger import logger
from database.crud import *
from services.tmdb_api import get_trending
router = Router()

@router.callback_query(F.data == "trending")
async def trending_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    logger.info(f"User {callback.message.chat.username} used /trending")

    builder = InlineKeyboardBuilder()

    builder.button(text="🎬 Movies", callback_data="trending:movie")
    builder.button(text="📺 TV Series", callback_data="trending:tv")
    builder.attach(back_button("menu"))
    builder.adjust(2, 1)

    await callback.message.edit_text(text="✨ Choose desired category", reply_markup=builder.as_markup())
    await state.set_state(SearchStates.waiting_for_category)

@router.callback_query(SearchStates.waiting_for_category, F.data.startswith("trending:"))
async def trending_category(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    trending_type = callback.data.split(":", 1)[1]

    result = await get_trending(trending_type)
    builder = InlineKeyboardBuilder()

    if result:
        for i in result[:10]:
            adult = " 🔞" if i.get("adult") else ""

            if i.get("media_type") == "movie":
                title = i.get("title")
                release = i.get("release_date")
                callback_answer = "movie_choice"

            elif i.get("media_type") == "tv":
                title = i.get("name")
                release = i.get("first_air_date")
                callback_answer = "series_choice"

            builder.button(text=f'{title}, {release.split("-")[0] or "????"}{adult}', callback_data=f"{callback_answer}:{i['id']}")

        builder.attach(back_button("trending"))
        builder.adjust(1)

        await callback.message.edit_text("✨ Choose your content:", reply_markup=builder.as_markup())

        await state.set_state(SearchStates.waiting_for_choice)
        await state.update_data(search_results=result)
        await state.update_data(parent="trending")