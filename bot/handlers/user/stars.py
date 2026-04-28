# bot/handlers/user/stars.py
"""Stars prices handler."""
from aiogram import Router, F
from aiogram.types import Message
from bot.config import settings
from bot.keyboards.user.stars import get_stars_keyboard

router = Router(name="stars")

@router.message(F.text == "⭐️Stars narxlari")
async def stars_prices(message: Message):
    text = """<b>Ishonchli va hamyonbop narxda, 100% kafolatli Telegram Stars 🤩</b>

<blockquote>⭐️ 50 Stars — 20,000 so'm
⭐️ 75 Stars — 25,000 so'm
⭐️ 100 Stars — 33,000 so'm
⭐️ 150 Stars — 49,000 so'm</blockquote>

<b>2-3 daqiqa ichida akkauntingizga Telegram Stars o'tkaziladi 🤝</b>

<i>💠 Qadirdonlaringizga hadya qilishingiz ham mumkin.</i>"""
    
    if settings.stars_file_id:
        await message.answer_photo(
            photo=settings.stars_file_id,
            caption=text,
            reply_markup=get_stars_keyboard(settings.admin_username),
            parse_mode="HTML"
        )
    else:
        await message.answer(text, reply_markup=get_stars_keyboard(settings.admin_username), parse_mode="HTML")