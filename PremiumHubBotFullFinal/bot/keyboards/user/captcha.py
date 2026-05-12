"""Captcha keyboard."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo


def get_captcha_keyboard(captcha_url: str) -> ReplyKeyboardMarkup:
    """Captcha WebApp keyboard.

    ReplyKeyboard ishlatilishi shart — faqat KeyboardButton bilan
    web_app_data xabari botga yetib keladi (InlineKeyboard bilan kelmaydi).
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔐 Captcha o'tish", web_app=WebAppInfo(url=captcha_url))]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
