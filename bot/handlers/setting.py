from aiogram import F, types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.keyboards.back_button import back_button
from bot.keyboards.languages import get_lang_menu
from bot.logger import logger
from bot.i18n import t, current_locale
from database.crud import *
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

async def get_locale_text(session: AsyncSession, user_id: id):
    locale = await get_locale(session, user_id)

    match locale:
        case "en-US":
            locale_text = t("language.chosen.en")
        case "es-ES":
            locale_text = t("language.chosen.es")
        case "fr-FR":
            locale_text = t("language.chosen.fr")
        case "de-DE":
            locale_text = t("language.chosen.de")
        case "ru-RU":
            locale_text = t("language.chosen.ru")

    return locale_text

def build_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text=t("settings.adult"), callback_data="adult")
    builder.button(text=t("settings.language"), callback_data="change_lang")
    builder.attach(back_button("menu"))
    builder.adjust(1)

    return builder

@router.callback_query(F.data == "settings")
async def settings_menu(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()

    logger.info(f"User {callback.message.chat.id} used /settings")

    if(await get_adult(session=session, telegram_id=callback.message.chat.id)):\
        text_adult=t("adult_status.true")
    else:
        text_adult=t("adult_status.false")

    locale_text = await get_locale_text(session, callback.message.chat.id)
    
    await callback.message.edit_text(
        text=(
            f"{t("settings.text")}\n\n"
            f"{text_adult}\n"
            f"{locale_text}\n"
        ),
        reply_markup=build_keyboard().as_markup(),
    )

    logger.info(f"User @{callback.message.chat.username} used /settings command")

@router.callback_query(F.data == "adult")
async def adult_switch(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()

    adult_user = await toggle_adult(session=session, telegram_id=callback.message.chat.id)

    logger.info(f"User {callback.message.chat.id} toggled adult mode to {adult_user}")

    text_adult = t("adult_status.true") if adult_user else t("adult_status.false")

    locale_text = await get_locale_text(session, callback.message.chat.id)

    await callback.message.edit_text(
        text=(
            f"{t("settings.text")}\n\n"
            f"{text_adult}\n"
            f"{locale_text}\n"
        ),
        reply_markup=build_keyboard().as_markup(),
    )

    logger.info(f"User @{callback.message.chat.username} changed his Adult Mode to {adult_user}")

@router.callback_query(F.data == "change_lang")
async def choose_language(callback: types.CallbackQuery):
    await callback.answer()

    await callback.message.edit_text(text=t("choose.language"), reply_markup=get_lang_menu())

@router.callback_query(F.data.startswith("lang"))
async def change_language(callback: types.CallbackQuery, session: AsyncSession):
    language = callback.data.split(":", 1)[1]
    if language == "none":
        await callback.answer(t("language.not_changed"))
        return

    await set_locale(session, callback.message.chat.id, language)

    token = current_locale.set(language)
    try:
        await callback.answer(t("language.changed"))
        
        adult_user = await toggle_adult(session=session, telegram_id=callback.message.chat.id)
        text_adult = t("adult_status.true") if adult_user else t("adult_status.false")
        locale_text = await get_locale_text(session, callback.message.chat.id)
        
        await callback.message.edit_text(
            f"{t('settings.text')}\n\n{text_adult}\n{locale_text}",
            reply_markup=build_keyboard().as_markup()
        )
    finally:
        current_locale.reset(token)