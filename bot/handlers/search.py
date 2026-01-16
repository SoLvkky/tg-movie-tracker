from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.states.search_states import SearchStates
from bot.keyboards.back_button import back_button
from bot.logger import logger
from database.crud import *
from services.tmdb_api import search_content
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.callback_query(F.data == "search")
async def process_search(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    logger.info(f"User @{callback.from_user.username} used /search")
    
    await callback.message.edit_text(text="🎬 Please send the title of the movie/series you want to find", reply_markup=back_button("menu").as_markup())
    await state.set_state(SearchStates.waiting_for_title)

@router.message(SearchStates.waiting_for_title, F.text)
async def process_title(message: types.Message, session: AsyncSession, state: FSMContext):
    title = message.text.strip()

    adult = await get_adult(session=session, telegram_id=message.chat.id)

    result = await search_content(title, adult)
    builder = InlineKeyboardBuilder()

    if result:
        for i in result[:5]:
            adult = " 🔞" if i.get("adult") else ""

            if i.get("media_type") == "movie":
                title = i.get("title")
                release = i.get("release_date")
                media_type = "MOVIE"
                callback_answer = "movie_choice"

            elif i.get("media_type") == "tv":
                title = i.get("name")
                release = i.get("first_air_date")
                media_type = "SERIES"
                callback_answer = "series_choice"

            builder.button(text=f'{media_type} | {title}, {release.split("-")[0] or "????"}{adult}', callback_data=f"{callback_answer}:{i['id']}")

        builder.attach(back_button("search"))
        builder.adjust(1)

        await message.answer("✨ Choose your movie/series:", reply_markup=builder.as_markup())

        await state.set_state(SearchStates.waiting_for_choice)
        await state.update_data(search_results=result)
        await state.update_data(parent="search")

    else:
        await message.answer("❌ Movie not found. Try a more precise name", reply_markup=back_button("search").as_markup())

        await state.set_state(SearchStates.waiting_for_title)

@router.message(SearchStates.waiting_for_title, ~F.text)
async def process_title_not_text(message: types.Message, state: FSMContext):
    await message.answer(
        "Please send the movie title as text (not a photo/sticker/voice message).",
        reply_markup=back_button("menu").as_markup(),
    )
