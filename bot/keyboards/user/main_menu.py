"""User main menu keyboards."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✨BEPUL PREMIUM OLISH💫")],
            [KeyboardButton(text="💸Premium narxlari"), KeyboardButton(text="⭐️Stars narxlari")],
            [KeyboardButton(text="👑TOP reyting")],
            [KeyboardButton(text="🎁Bonus olish"), KeyboardButton(text="💳Mening hisobim")],
            [KeyboardButton(text="📝Qo'llanma"), KeyboardButton(text="👮🏽Administrator")]
        ],
        resize_keyboard=True
    )


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Phone number request keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon raqamingizni yuborish", request_contact=True)]
        ],
        resize_keyboard=True
    )