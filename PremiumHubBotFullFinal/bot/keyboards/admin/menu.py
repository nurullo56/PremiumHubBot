"""Admin main menu keyboards."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_admin_main_keyboard() -> ReplyKeyboardMarkup:
    """Admin main menu keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ Kanal qo'shish"),
                KeyboardButton(text="➖ Kanal o'chirish")
            ],
            [
                KeyboardButton(text="🔍 Kanal ma'lumotlari"),
                KeyboardButton(text="📃 Kanal ro'yxati")
            ],
            [
                KeyboardButton(text="📊 Statistika"),
                KeyboardButton(text="👤 Foydalanuvchilar")
            ],
            [
                KeyboardButton(text="📩 Xabar yuborish"),
                KeyboardButton(text="🎟 Promokodlar")
            ],
            [
                KeyboardButton(text="⭐ Premium so'rovlar"),
                KeyboardButton(text="📃 Zayavkalar ro'yxati")
            ],
            [
                KeyboardButton(text="➕ Zayavka qo'shish"),
                KeyboardButton(text="➖ Zayavka o'chirish")
            ],
            [
                KeyboardButton(text="🔍 Chat ID aniqlash")
            ],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Admin amalini tanlang..."
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Cancel action keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )


def get_confirmation_keyboard() -> ReplyKeyboardMarkup:
    """Confirmation keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="✅ Ha"),
            KeyboardButton(text="❌ Yo'q")
        ]],
        resize_keyboard=True
    )
