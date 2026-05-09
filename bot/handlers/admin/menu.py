"""Admin menu handler."""

import logging
from aiogram import Router, F
from bot.filters import IsAdmin
from aiogram.types import Message
from aiogram.filters import Command

from bot.config import settings
from bot.keyboards.admin.menu import get_admin_main_keyboard
from bot.keyboards.user.main_menu import get_main_keyboard
from bot.texts.admin.messages import ADMIN_MENU

logger = logging.getLogger(__name__)
router = Router(name="admin_menu")


@router.message(IsAdmin(), Command("admin"))
@router.message(IsAdmin(), F.text == "⚙️ Admin panel")
async def show_admin_menu(message: Message):
    """Show admin panel."""
    await message.answer(
        ADMIN_MENU,
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(IsAdmin(), F.text == "🔙 Orqaga")
async def back_to_user_panel(message: Message):
    """Admin paneldan foydalanuvchi paneliga qaytish."""
    await message.answer(
        "👤 <b>Foydalanuvchi paneli</b>",
        reply_markup=get_main_keyboard(is_admin=True),
        parse_mode="HTML"
    )
