"""Top rating - leaderboard system."""

import logging
from typing import List, Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from bot.database.repositories.referral_repo import referral_repo
from bot.keyboards.user.top_rating import get_top_rating_keyboard
from bot.config import settings

logger = logging.getLogger(__name__)
router = Router(name="top_rating")


async def get_top_referrers(limit: int = 20) -> List[Dict[str, Any]]:
    try:
        if hasattr(referral_repo, 'get_top_referrers'):
            return await referral_repo.get_top_referrers(limit)
        return []
    except Exception as e:
        logger.error(f"Top referrers error: {e}")
        return []


async def get_weekly_top_referrers(limit: int = 10) -> List[Dict[str, Any]]:
    try:
        if hasattr(referral_repo, 'get_top_referrers_by_period'):
            return await referral_repo.get_top_referrers_by_period(7, limit)
        if hasattr(referral_repo, 'get_top_referrers'):
            return await referral_repo.get_top_referrers(limit)
        return []
    except Exception as e:
        logger.error(f"Weekly top error: {e}")
        return []


def format_leaderboard(users: List[Dict], title: str, footer: str, limit: int) -> str:
    text = f"{title}\n\n"
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    
    for i, user in enumerate(users[:limit], 1):
        medal = medals.get(i, f"{i}.")
        username = user.get('username') if isinstance(user, dict) else getattr(user, 'username', None)
        fullname = user.get('fullname', 'N/A') if isinstance(user, dict) else getattr(user, 'fullname', 'N/A')
        count = user.get('referral_count', 0) if isinstance(user, dict) else getattr(user, 'referral_count', 0)
        
        text += f"{medal} <b>{fullname}</b>"
        if username:
            text += f" (@{username})"
        text += f"\n   👥 Do'stlar: {count}\n\n"
    
    text += f"\n{footer}"
    return text


async def safe_edit(callback: CallbackQuery, text: str):
    try:
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=text,
                reply_markup=get_top_rating_keyboard()
            )
        else:
            await callback.message.edit_text(
                text=text,
                reply_markup=get_top_rating_keyboard()
            )
    except TelegramBadRequest:
        pass


@router.message(F.text == "👑TOP reyting")
async def show_top_rating(message: Message):
    text = (
        "🎉 <b>TOP REYTINGLAR</b>\n\n"
        "Haftalik va oylik konkurslarda qatnashing, "
        "Telegram Premium va Telegram stars⭐️ yutib oling! 🎁"
    )
    
    top_file_id = getattr(settings, 'top_file_id', None)
    
    if top_file_id:
        await message.answer_photo(
            photo=top_file_id,
            caption=text,
            reply_markup=get_top_rating_keyboard()
        )
    else:
        await message.answer(text, reply_markup=get_top_rating_keyboard())


@router.callback_query(F.data == "top_all")
async def show_top_all(callback: CallbackQuery):
    await callback.answer()
    
    users = await get_top_referrers(20)
    
    if not users:
        await safe_edit(callback, "📋 Hozircha ma'lumot yo'q")
        return
    
    text = format_leaderboard(
        users=users,
        title="🏆 <b>TOP 20 FOYDALANUVCHILAR</b>",
        footer="💡 <i>Ko'proq do'st taklif qiling va TOP da bo'ling!</i>",
        limit=20
    )
    
    await safe_edit(callback, text)


@router.callback_query(F.data == "top_weekly")
async def show_top_weekly(callback: CallbackQuery):
    await callback.answer()
    
    users = await get_weekly_top_referrers(10)
    
    if not users:
        await safe_edit(callback, "📋 Hozircha ma'lumot yo'q")
        return
    
    text = format_leaderboard(
        users=users,
        title="🏆 <b>TOP 10 HAFTALIK FOYDALANUVCHILAR</b>",
        footer="💡 <i>Bu hafta ko'proq do'st taklif qiling!</i>",
        limit=10
    )
    
    await safe_edit(callback, text)