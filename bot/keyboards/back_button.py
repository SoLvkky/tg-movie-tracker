from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.i18n import t

def back_button(callback_data: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=t("go_back"), callback_data=callback_data)
    builder.adjust(1)

    return builder