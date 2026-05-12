"""Guide keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_guide_keyboard() -> InlineKeyboardMarkup:
    """Get main guide menu keyboard."""
    builder = InlineKeyboardBuilder()
    
    buttons = [
        ("✨ Premium olish", "guide_premium"),
        ("💸 Premium narxlari", "guide_prices"),
        ("⭐️ Stars narxlari", "guide_stars"),
        ("🎁 Bonus", "guide_bonus"),
        ("👑 TOP reyting", "guide_rating"),
        ("💳 Hisob va to'lovlar", "guide_balance"),
    ]
    
    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)
    
    # 2 qatorga joylashtirish
    builder.adjust(2)
    
    return builder.as_markup()


def get_guide_section_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for guide section (with back button)."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🔙 Orqaga", callback_data="guide_back")
    
    return builder.as_markup()