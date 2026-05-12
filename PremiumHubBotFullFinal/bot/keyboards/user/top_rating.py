from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_top_rating_keyboard() -> InlineKeyboardMarkup:
    """Get top rating inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏆 Barcha vaqt", callback_data="top_all"),
                InlineKeyboardButton(text="📅 Haftalik", callback_data="top_weekly")
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_profile")
            ]
        ]
    )