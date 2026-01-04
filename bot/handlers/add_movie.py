from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.states.movie_states import MovieStates
from bot.keyboards.main_menu import get_main_menu
from bot.logger import logger
from database.crud import *
from services.tmdb_api import search_movie

router = Router()

def back_button(callback_data: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="GO BACK", callback_data=callback_data)
    builder.adjust(1)

    return builder

@router.callback_query(lambda c: c.data == "menu")
async def go_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        text="Choose your option:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "add_movie")
async def process_add_movie(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"User @{callback.from_user.username} used /add_movie command")
    await callback.message.edit_text(text="Send the title of the movie you want to add 🎬", reply_markup=back_button("menu").as_markup())
    await state.set_state(MovieStates.waiting_for_title)
    await callback.answer()

@router.message(MovieStates.waiting_for_title, F.text)
async def process_movie_title(message: types.Message, state: FSMContext):
    title = message.text.strip()

    result = await search_movie(query=title)
    builder = InlineKeyboardBuilder()

    if result:
        for i in result:
            adult = ", 18+ ONLY" if i.get("adult") else ""
            builder.button(text=f'{i.get("original_title")}, {i.get("release_date").split("-")[0] or "????"}{adult}', callback_data=str(i["id"]))
        builder.attach(back_button("add_movie"))
        builder.adjust(1)

        await message.answer("Choose your movie:", reply_markup=builder.as_markup())

        await state.set_state(MovieStates.waiting_for_choice)
        await state.update_data(search_results=result)
        await state.update_data(parent="add_movie")

    else:
        await message.answer("Movie not found. Try a more precise name", reply_markup=back_button("add_movie").as_markup())

        await state.set_state(MovieStates.waiting_for_title)

@router.message(MovieStates.waiting_for_title, ~F.text)
async def process_movie_title_not_text(message: types.Message, state: FSMContext):
    await message.answer(
        "Please send the movie title as text (not a photo/sticker/voice message).",
        reply_markup=back_button("menu").as_markup(),
    )
