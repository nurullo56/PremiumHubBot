"""Admin menu handler."""

import logging
from aiogram import Router, F
from bot.filters import IsAdmin
from aiogram.types import Message
from aiogram.filters import Command

from bot.keyboards.admin.menu import get_admin_main_keyboard
from bot.texts.admin.messages import ADMIN_MENU

logger = logging.getLogger(__name__)
router = Router(name="admin_menu")


@router.message(IsAdmin(), Command("admin"))
async def show_admin_menu(message: Message):
    """Show admin panel."""
    await message.answer(
        ADMIN_MENU,
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(IsAdmin(), F.text == "🔙 Orqaga")
async def back_to_admin_menu(message: Message):
    """Back to admin menu."""
    await show_admin_menu(message)
