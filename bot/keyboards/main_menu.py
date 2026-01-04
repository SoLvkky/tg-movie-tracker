from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Search", callback_data="add_movie")],
            [InlineKeyboardButton(text="📋 My Movies", callback_data="my_movies"), InlineKeyboardButton(text="📊 Stats", callback_data="stats")]
        ],
        resize_keyboard=True
    )