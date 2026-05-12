"""Admin promocode keyboards."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_promocode_management_keyboard() -> ReplyKeyboardMarkup:
    """Promocode management keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Promokodlar statistikasi")],
            [
                KeyboardButton(text="➕ Promokod yaratish"),
                KeyboardButton(text="💎 Promokod tekshirish")
            ],
            [
                KeyboardButton(text="📋 Barcha promokodlar"),
                KeyboardButton(text="🗑 Promokod o'chirish")
            ],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )
