"""Admin broadcast keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_broadcast_target_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Hammaga", callback_data="broadcast_all")],
            [InlineKeyboardButton(text="👨 Erkaklarga", callback_data="broadcast_male")],
            [InlineKeyboardButton(text="👩 Ayollarga", callback_data="broadcast_female")],
            [InlineKeyboardButton(text="⭐ Premium foydalanuvchilarga", callback_data="broadcast_premium")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel")],
        ]
    )


def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yuborish", callback_data="broadcast_confirm"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel"),
            ]
        ]
    )
