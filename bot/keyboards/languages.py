from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.i18n import t

def get_lang_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("language.set.en"), callback_data="lang:en-US")],
            [InlineKeyboardButton(text=t("language.set.es"), callback_data="lang:es-ES")],
            [InlineKeyboardButton(text=t("language.set.fr"), callback_data="lang:fr-FR")],
            [InlineKeyboardButton(text=t("language.set.de"), callback_data="lang:de-DE")],
            [InlineKeyboardButton(text=t("language.set.ru"), callback_data="lang:ru-RU")],
            [InlineKeyboardButton(text=t("go_back"), callback_data="settings")]
        ],
        resize_keyboard=True
    )