"""Gender selection keyboard."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Gender selection inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Erkak", callback_data="gender_male"),
                InlineKeyboardButton(text="👩 Ayol", callback_data="gender_female")
            ]
        ]
    )
