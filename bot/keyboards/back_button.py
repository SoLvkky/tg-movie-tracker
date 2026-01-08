from aiogram.utils.keyboard import InlineKeyboardBuilder

def back_button(callback_data: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="GO BACK", callback_data=callback_data)
    builder.adjust(1)

    return builder