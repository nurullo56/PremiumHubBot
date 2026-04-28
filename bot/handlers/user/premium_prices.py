"""Premium prices and purchase info."""

import logging
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import settings

logger = logging.getLogger(__name__)
router = Router(name="premium_prices")


def get_premium_purchase_keyboard() -> InlineKeyboardMarkup:
    """Premium purchase keyboard."""
    buttons = []
    
    if settings.admin_username:
        buttons.append([
            InlineKeyboardButton(
                text="👤 Admin bilan bog'lanish",
                url=f"https://t.me/{settings.admin_username.lstrip('@')}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "💸Premium narxlari")
async def show_premium_prices(message: Message):
    """Show premium prices."""
    text = (
        "💎 <b>PREMIUM NARXLARI</b>\n\n"
        "<b>Profilga kirish orqali:</b>\n"
        "▪️ 1 oylik obuna — 50,000 so'm\n"
        "▪️ 12 oylik obuna — 299,000 so'm\n\n"
        "<b>Profilga kirmasdan (Sovg'a):</b>\n"
        "▪️ 3 oylik — 175,000 so'm\n"
        "▪️ 6 oylik — 225,000 so'm\n"
        "▪️ 12 oylik — 399,000 so'm\n\n"
        "💡 <i>Premium sotib olish uchun admin bilan bog'laning.</i>"
    )
    
    # If premium_file_id is set, send as photo
    if settings.premium_file_id:
        await message.answer_photo(
            photo=settings.premium_file_id,
            caption=text,
            reply_markup=get_premium_purchase_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            text,
            reply_markup=get_premium_purchase_keyboard(),
            parse_mode="HTML"
        )
