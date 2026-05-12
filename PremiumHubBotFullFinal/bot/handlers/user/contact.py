# bot/handlers/user/contact.py
"""Contact admin handler."""
from aiogram import Router, F
from aiogram.types import Message
from bot.config import settings

router = Router(name="contact")

@router.message(F.text == "👮🏽Administrator")
async def contact_admin(message: Message):
    await message.answer(
        f"📞 Administrator bilan bog'lanish:\n@{settings.admin_username}",
        parse_mode="HTML"
    )