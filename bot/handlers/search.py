from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.states.search_states import SearchStates
from bot.keyboards.back_button import back_button
from bot.logger import logger
from bot.i18n import t
from database.crud import *
from services.tmdb_api import search_content
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

@router.callback_query(F.data == "search")
async def process_search(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    logger.info(f"User @{callback.from_user.username} used /search")
    
    await callback.message.edit_text(text=t("search_title"), reply_markup=back_button("menu").as_markup())
    await state.set_state(SearchStates.waiting_for_title)

@router.message(SearchStates.waiting_for_title, F.text)
async def process_title(message: types.Message, session: AsyncSession, state: FSMContext):
    title = message.text.strip()
    lang = await get_locale(session, message.chat.id)
    adult = await get_adult(session=session, telegram_id=message.chat.id)

    result = await search_content(title, adult, lang)
    builder = InlineKeyboardBuilder()

    if result:
        for i in result[:10]:
            adult = " 🔞" if i.get("adult") else ""

            match i.get("media_type"):
                case "movie":
                    title, release, media_type, c_data = i.get("title"), i.get("release_date"), t("type_movie"), "movie_choice"
                case "tv":
                    title, release, media_type, c_data = i.get("name"), i.get("first_air_date"), t("type_tv"), "tv_choice"

            builder.button(text=f'{media_type} | {title}, {release.split("-")[0] or "????"}{adult}', callback_data=f"{c_data}:{i.get('id')}")

        builder.attach(back_button("search"))
        builder.adjust(1)

        await message.answer(text=t("choose.content"), reply_markup=builder.as_markup())

        await state.set_state(SearchStates.waiting_for_choice)
        await state.update_data(search_results=result)
        await state.update_data(parent="search")

    else:
        await message.answer(t("search_not_found"), reply_markup=back_button("search").as_markup())

        await state.set_state(SearchStates.waiting_for_title)

@router.message(SearchStates.waiting_for_title, ~F.text)
async def process_title_not_text(message: types.Message, state: FSMContext):
    await message.answer(
        text=t("search_wrong_type"),
        reply_markup=back_button("menu").as_markup(),
    )
