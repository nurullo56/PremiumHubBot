# bot/handlers/user/referral.py
"""Bepul Premium - Referral tizimi orqali"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import settings
from bot.services.referral.referral_service import referral_service
from bot.database.repositories.user_repo import user_repo

router = Router(name="referral_premium")
logger = logging.getLogger(__name__)


# ===================== KLAVIATURALAR =====================

def get_referral_keyboard(user_id: int):
    """Referral klaviaturasi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Do'stlarga ulashish",
                    switch_inline_query=f"Menga qo'shiling! https://t.me/{settings.bot_username}?start={user_id}"
                )
            ],
            [
                InlineKeyboardButton(text="📋 Mening do'stlarim", callback_data="my_friends")
            ],
            [
                InlineKeyboardButton(text="🔄 Yangilash", callback_data="refresh_premium")
            ]
        ]
    )


def get_friends_keyboard():
    """Do'stlar ro'yxatidan qaytish"""
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_premium")
        ]]
    )


# ===================== MATN GENERATOR =====================

def get_referral_status_text(count: int, required: int, referral_link: str, remaining: int, percent: int):
    """Premium sahifasi matni"""
    bars = min(int(count / required * 10), 10)
    progress = "🟩" * bars + "⬜️" * (10 - bars)
    
    return (
        "💎 <b>BEPUL Telegram Premium olish</b>\n\n"
        f"👥 Taklif qilingan: <b>{count}</b>\n"
        f"🎯 Kerakli: <b>{required}</b>\n"
        f"⏳ Qoldi: <b>{remaining}</b>\n\n"
        f"📊 {progress} {percent}%\n\n"
        f"🔗 <b>Referral havolangiz:</b>\n"
        f"<code>{referral_link}</code>\n\n"
        f"💡 Do'stlaringizni taklif qiling va {required} taga yetganda "
        "💳 Mening hisobim bo'limidan Premium sotib oling!"
    )


def get_friends_list_text(friends: list):
    """Do'stlar ro'yxati matni"""
    total = len(friends)
    text = f"👥 <b>Do'stlaringiz ({total} ta):</b>\n\n"
    
    for i, friend in enumerate(friends[:20], 1):
        username_str = f"@{friend['username']}" if friend.get('username') else "❌"
        text += f"{i}. {friend['fullname']} ({username_str})\n"
    
    if total > 20:
        text += f"\n... va yana {total - 20} ta"
    
    return text


# ===================== HANDLERLAR =====================

@router.message(F.text == "✨BEPUL PREMIUM OLISH💫")
async def bepul_premium_handler(message: Message):
    """Bepul Premium - Referral bonus berish va status ko'rsatish"""
    user_id = message.from_user.id
    fullname = message.from_user.full_name
    
    logger.info(f"🔵 BEPUL PREMIUM: user_id={user_id}, name={fullname}")
    
    try:
        # 🎯 REFERRAL BONUS BERISH (agar hali berilmagan bo'lsa)
        user = await user_repo.get_by_id(user_id)
        if user and user.get('referred_by') and not user.get('referral_bonus_given'):
            try:
                from bot.database.repositories.referral_bonus_repo import give_referral_bonus
                from bot.utils.bot.instance import bot_instance
                
                success, msg = await give_referral_bonus(
                    user['referred_by'], 
                    user_id, 
                    fullname, 
                    bot_instance.get()
                )
                if success:
                    logger.info(f"✅ Manual bonus given: {user['referred_by']} <- {user_id}")
                else:
                    logger.warning(f"⚠️ Manual bonus failed: {msg}")
            except Exception as e:
                logger.error(f"❌ Manual bonus error: {e}")
        
        # Status olish
        status = await referral_service.get_status(user_id)
        
        text = get_referral_status_text(
            count=status['count'],
            required=settings.required_referrals,
            referral_link=status['link'],
            remaining=status['remaining'],
            percent=status['percent']
        )
        
        keyboard = get_referral_keyboard(user_id)

        if settings.premium_file_id:
            await message.answer_photo(
                photo=settings.premium_file_id,
                caption=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await message.answer(
                text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"❌ PREMIUM XATO: {e}", exc_info=True)
        await message.answer("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")


@router.callback_query(F.data == "refresh_premium")
async def refresh_premium_callback(callback: CallbackQuery):
    """Premium sahifasini yangilash"""
    status = await referral_service.get_status(callback.from_user.id)
    
    text = get_referral_status_text(
        count=status['count'],
        required=settings.required_referrals,
        referral_link=status['link'],
        remaining=status['remaining'],
        percent=status['percent']
    )
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=get_referral_keyboard(callback.from_user.id),
            parse_mode="HTML"
        )
    except:
        try:
            await callback.message.edit_text(
                text=text,
                reply_markup=get_referral_keyboard(callback.from_user.id),
                parse_mode="HTML"
            )
        except:
            pass
    
    await callback.answer("🔄 Yangilandi!")


@router.callback_query(F.data == "my_friends")
async def my_friends_callback(callback: CallbackQuery):
    """Do'stlar ro'yxati"""
    user_id = callback.from_user.id
    friends = await referral_service.get_friends_list(user_id)
    
    if not friends:
        await callback.answer("❌ Sizda hali do'stlar yo'q", show_alert=True)
        return
    
    text = get_friends_list_text(friends)
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=get_friends_keyboard(),
            parse_mode="HTML"
        )
    except:
        await callback.message.edit_text(
            text=text,
            reply_markup=get_friends_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data == "back_to_premium")
async def back_to_premium_callback(callback: CallbackQuery):
    """Premium sahifasiga qaytish"""
    status = await referral_service.get_status(callback.from_user.id)
    
    text = get_referral_status_text(
        count=status['count'],
        required=settings.required_referrals,
        referral_link=status['link'],
        remaining=status['remaining'],
        percent=status['percent']
    )
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=get_referral_keyboard(callback.from_user.id),
            parse_mode="HTML"
        )
    except:
        await callback.message.edit_text(
            text=text,
            reply_markup=get_referral_keyboard(callback.from_user.id),
            parse_mode="HTML"
        )
    
    await callback.answer()