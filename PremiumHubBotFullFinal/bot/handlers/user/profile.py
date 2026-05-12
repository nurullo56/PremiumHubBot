"""Profile and balance handlers."""

import logging
from decimal import Decimal

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from bot.database.repositories.user_repo import user_repo
from bot.services.finance.balance_service import balance_service
from bot.services.referral.referral_service import referral_service
from bot.keyboards.user.profile import (
    get_profile_keyboard,
    get_balance_keyboard,
    get_referral_keyboard
)
from bot.texts.user.messages import PROFILE_INFO, BALANCE_INFO, REFERRAL_INFO
from bot.utils.common.timezone import format_for_display, parse_uzbek_datetime
from bot.config import settings

logger = logging.getLogger(__name__)
router = Router(name="profile")


# ==================== MAIN PROFILE ====================

@router.message(F.text == "💳Mening hisobim")
async def show_profile(message: Message):
    """Show user profile with spending option."""
    user_id = message.from_user.id
    
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi!")
        return
    
    balance = await balance_service.get_balance(user_id)
    referral_count = await referral_service.get_referral_count(user_id)
    
    premium_status = "⭐ Premium" if user.get('premium_status') == 'active' else "🆓 Oddiy"
    
    reg_date = user.get('registration_date', '')
    reg_formatted = format_for_display(parse_uzbek_datetime(reg_date)) if reg_date else "Noma'lum"
    
    username_display = user.get('username') or "yo'q"
    
    text = f"""
✨ <b>Mening Hisobim</b>
_________________

👤 <b>Ism:</b> {user.get('fullname', 'N/A')}
🆔 <b>ID:</b> <code>{user_id}</code>
📱 <b>Username:</b> @{username_display}
💎 <b>Premium:</b> {premium_status}
_________________

💰 <b>Balans:</b> {await balance_service.format_balance(balance)} 💎
👥 <b>Referrallar:</b> {referral_count}
📅 <b>Ro'yxatdan o'tgan:</b> {reg_formatted}
_________________

<i>💡 Premium va Stars uchun sarflash tugmasi orqali siz o'z balansingizdagi mablag'ni ishlatishingiz mumkin.</i>
"""
    
    await message.answer(text, reply_markup=get_profile_keyboard(), parse_mode="HTML")


# ==================== BALANCE ====================

@router.callback_query(F.data == "profile_balance")
async def show_balance(callback: CallbackQuery):
    """Show balance details."""
    user_id = callback.from_user.id
    
    balance = await balance_service.get_balance(user_id)
    history = await balance_service.get_history(user_id, limit=10)
    
    history_text = ""
    if history:
        for item in history[:5]:
            amount = Decimal(str(item['amount']))
            formatted = await balance_service.format_balance(abs(amount))
            sign = "+" if amount > 0 else "-"
            desc = item.get('description', 'N/A')
            history_text += f"{sign}{formatted} - {desc}\n"
    else:
        history_text = "Tarix bo'sh"
    
    text = BALANCE_INFO.format(
        balance=await balance_service.format_balance(balance),
        history=history_text
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_balance_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# ==================== REFERRALS ====================

@router.callback_query(F.data == "profile_referrals")
async def show_referrals(callback: CallbackQuery):
    """Show referral info."""
    user_id = callback.from_user.id
    
    referral_count = await referral_service.get_referral_count(user_id)
    
    from bot.config.constants import BONUS_AMOUNT
    
    # ✅ FIXED: Calculate with Decimal for precision
    bonus_total = float(Decimal(str(referral_count)) * Decimal(str(BONUS_AMOUNT)))
    
    text = REFERRAL_INFO.format(
        referral_link=f"https://t.me/{settings.bot_username}?start={user_id}",
        total_referrals=referral_count,
        bonus_amount=bonus_total,
        bonus_per_user=BONUS_AMOUNT
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_referral_keyboard(settings.bot_username, user_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "my_referrals")
async def show_my_referrals(callback: CallbackQuery):
    """Show list of referred users."""
    user_id = callback.from_user.id
    
    referrals = await referral_service.get_referred_users(user_id, limit=20)
    
    if not referrals:
        await callback.answer("Sizda hali referrallar yo'q!", show_alert=True)
        return
    
    text = "👥 <b>SIZNING REFERRALLARINGIZ</b>\n\n"
    
    for idx, ref in enumerate(referrals[:10], 1):
        username = ref.get('username') or "yo'q"
        text += f"{idx}. {ref.get('fullname', 'N/A')} (@{username})\n"
    
    if len(referrals) > 10:
        text += f"\n... va yana {len(referrals) - 10} ta"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


# ==================== NAVIGATION ====================

@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery):
    """Navigate back to profile."""
    user_id = callback.from_user.id
    
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        await callback.answer("❌ Xatolik!", show_alert=True)
        return
    
    balance = await balance_service.get_balance(user_id)
    referral_count = await referral_service.get_referral_count(user_id)
    
    premium_status = "⭐ Premium" if user.get('premium_status') == 'active' else "🆓 Oddiy"
    
    reg_date = user.get('registration_date', '')
    reg_formatted = format_for_display(parse_uzbek_datetime(reg_date)) if reg_date else "Noma'lum"
    
    username_display = user.get('username') or "yo'q"
    
    text = f"""
✨ <b>Mening Hisobim</b>
_________________

👤 <b>Ism:</b> {user.get('fullname', 'N/A')}
🆔 <b>ID:</b> <code>{user_id}</code>
📱 <b>Username:</b> @{username_display}
💎 <b>Premium:</b> {premium_status}
_________________

💰 <b>Balans:</b> {await balance_service.format_balance(balance)} 💎
👥 <b>Referrallar:</b> {referral_count}
📅 <b>Ro'yxatdan o'tgan:</b> {reg_formatted}
_________________

<i>💡 Premium va Stars uchun sarflash tugmasi orqali siz o'z balansingizdagi mablag'ni ishlatishingiz mumkin.</i>
"""
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_profile_keyboard(),
            parse_mode="HTML"
        )
    except:
        await callback.message.answer(
            text,
            reply_markup=get_profile_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Navigate back to main menu."""
    from bot.keyboards.user.main_menu import get_main_keyboard
    
    await callback.message.answer(
        "🏠 Asosiy menyu",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()