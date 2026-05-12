# bot/handlers/user/bonus.py
"""Bonus handler."""
from aiogram import Router, F
from aiogram.types import Message

router = Router(name="bonus")

@router.message(F.text == "🎁Bonus olish")
async def bonus_handler(message: Message):
    await message.answer(
        "🔧 <b>Texnik ishlar olib borilmoqda</b>\n\n"
        "Bu bo'lim hozirda ishlab chiqilmoqda.\n"
        "Tez orada ishga tushiriladi!\n\n"
        "⏰ Keyinroq qaytib keling.",
        parse_mode="HTML"
    )