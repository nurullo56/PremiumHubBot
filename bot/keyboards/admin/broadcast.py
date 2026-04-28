"""Admin broadcast keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_broadcast_target_keyboard() -> InlineKeyboardMarkup:
    """Broadcast target selection keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Hammaga yuborish", callback_data="broadcast_all")],
            [InlineKeyboardButton(text="⭐ Premium foydalanuvchilarga", callback_data="broadcast_premium")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel")]
        ]
    )


def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    """Broadcast confirmation keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yuborish", callback_data="broadcast_confirm"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel")
            ]
        ]
    )
