from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.states.search_states import SearchStates
from bot.keyboards.back_button import back_button
from bot.logger import logger
from bot.i18n import t
from database.crud import *
from services.tmdb_api import get_trending
router = Router()

@router.callback_query(F.data == "trending")
async def trending_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    logger.info(f"User {callback.message.chat.username} used /trending")

    builder = InlineKeyboardBuilder()

    builder.button(text=t("trending.choose.movies"), callback_data="trending:movie")
    builder.button(text=t("trending.choose.tv"), callback_data="trending:tv")
    builder.attach(back_button("menu"))
    builder.adjust(2, 1)

    await callback.message.edit_text(text=t("choose.category"), reply_markup=builder.as_markup())
    await state.set_state(SearchStates.waiting_for_category)

@router.callback_query(SearchStates.waiting_for_category, F.data.startswith("trending:"))
async def trending_category(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    trending_type = callback.data.split(":", 1)[1]
    lang = await get_locale(session, callback.message.chat.id)

    result = await get_trending(trending_type, lang)
    builder = InlineKeyboardBuilder()

    if result:
        for i in result[:10]:
            adult = " 🔞" if i.get("adult") else ""

            match i.get("media_type"):
                case "movie":
                    title, release, c_data = i.get("title"), i.get("release_date"), "movie_choice"
                case "tv":
                    title, release, c_data = i.get("name"), i.get("first_air_date"),"tv_choice"

            builder.button(text=f'{title}, {release.split("-")[0] or "????"}{adult}', callback_data=f"{c_data}:{i['id']}")

        builder.attach(back_button("trending"))
        builder.adjust(1)

        await callback.message.edit_text(t("choose.content"), reply_markup=builder.as_markup())

        await state.set_state(SearchStates.waiting_for_choice)
        await state.update_data(search_results=result)
        await state.update_data(parent="trending")