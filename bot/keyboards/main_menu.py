from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.i18n import t

def get_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("menu.search"), callback_data="search")],
            [InlineKeyboardButton(text=t("menu.trending"), callback_data="trending")],
            [InlineKeyboardButton(text=t("menu.collection"), callback_data="my_collection")], 
            [InlineKeyboardButton(text=t("menu.stats"), callback_data="stats")],
            [InlineKeyboardButton(text=t("menu.settings"), callback_data="settings")]
        ],
        resize_keyboard=True
    )