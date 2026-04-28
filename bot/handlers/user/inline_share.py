# bot/handlers/user/inline_share.py
"""Inline mode handler for sharing referral links."""

from typing import Dict, List, Tuple, Optional, Any
import logging
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import settings

logger = logging.getLogger(__name__)
router = Router(name="inline_share")


@router.inline_query()
async def inline_share_handler(query: types.InlineQuery):
    """
    Handle inline queries for sharing referral links.
    
    Usage: @bot_username any text
    """
    user_id = query.from_user.id
    referral_link = f"https://t.me/{settings.bot_username}?start={user_id}"
    
    # Inline keyboard
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💎 BEPUL Premium olish",
                    url=referral_link
                )
            ]
        ]
    )
    
    # Message text
    message_text = (
        "🎁 <b>BEPUL TELEGRAM PREMIUM OLISH IMKONIYATI!</b>\n\n"
        "Men ushbu bot orqali do'stlarimni taklif qilib, "
        "bepul Telegram Premium oldim va sizga ham tavsiya qilaman!\n\n"
        "💎 40 ta do'stingizni taklif qiling va siz ham bepul premium oling!\n\n"
        "Agar siz ham bepul premium xizmatdan foydalanmoqchi bo'lsangiz, "
        "quyidagi tugmani bosing 👇"
    )
    
    results = [
        types.InlineQueryResultArticle(
            id="premium_link",
            title="💎 BEPUL Telegram Premium",
            description="Do'stlaringizga ulashing va premium oling!",
            thumbnail_url="https://telegram.org/img/tgme/icon_share.png",
            input_message_content=types.InputTextMessageContent(
                message_text=message_text,
                parse_mode="HTML"
            ),
            reply_markup=inline_keyboard,
        )
    ]
    
    await query.answer(results, cache_time=300, is_personal=True)


__all__ = ["router"]