from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Search", callback_data="search")],
            [InlineKeyboardButton(text="✨ Trending", callback_data="trending")],
            [InlineKeyboardButton(text="📋 My Collection", callback_data="my_collection")], 
            [InlineKeyboardButton(text="📊 Stats", callback_data="stats")],
            [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
        ],
        resize_keyboard=True
    )