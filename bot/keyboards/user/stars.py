"""Stars keyboard - inline keyboard for stars purchase."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_stars_kb(admin_username: str = None) -> InlineKeyboardMarkup:
    """Stars sotib olish klaviaturasi"""
    # @ belgisini olib tashlash
    clean_username = admin_username.replace('@', '') if admin_username else ""
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐️ Stars sotib olish",
                    url=f"https://t.me/{clean_username}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data="back_to_profile"
                )
            ]
        ]
    )
    return keyboard


def get_starspremium_kb(admin_username: str = None) -> InlineKeyboardMarkup:
    """Premium sotib olish klaviaturasi"""
    # @ belgisini olib tashlash
    clean_username = admin_username.replace('@', '') if admin_username else ""
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌟 Premium sotib olish",
                    url=f"https://t.me/{clean_username}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data="back_to_profile"
                )
            ]
        ]
    )
    return keyboard


# Eski nom bilan moslik uchun (agar stars.py da get_stars_keyboard deb chaqirilayotgan bo'lsa)
get_stars_keyboard = get_stars_kb