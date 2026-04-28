"""Captcha keyboard."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_captcha_keyboard(captcha_url: str) -> InlineKeyboardMarkup:
    """Captcha WebApp keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔐 Captcha o'tish", web_app={"url": captcha_url})]
        ]
    )
