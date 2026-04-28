"""Premium requests management."""

import logging
from aiogram import Router, F
from bot.filters import IsAdmin
from aiogram.types import Message, CallbackQuery

from bot.services.premium.premium_service import premium_service
from bot.database.repositories.user_repo import user_repo
from bot.keyboards.admin.user_management import (
    get_premium_requests_keyboard,
    get_premium_action_keyboard
)

logger = logging.getLogger(__name__)
router = Router(name="premium_requests")


@router.message(IsAdmin(), F.text == "⭐ Premium so'rovlar")
async def show_premium_requests(message: Message):
    """Show pending premium requests."""
    requests = await premium_service.get_pending_requests()
    
    if not requests:
        await message.answer(
            "📭 <b>PREMIUM SO'ROVLAR</b>\n\n"
            "Hozircha so'rovlar yo'q.",
            parse_mode="HTML"
        )
        return
    
    await message.answer(
        f"⭐ <b>PREMIUM SO'ROVLAR</b>\n\n"
        f"Jami: {len(requests)} ta\n\n"
        f"Foydalanuvchini tanlang:",
        reply_markup=get_premium_requests_keyboard(requests),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("premium_view:"))
async def view_premium_request(callback: CallbackQuery):
    """View premium request details."""
    user_id = int(callback.data.split(":")[1])
    
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
        return
    
    from bot.services.finance.balance_service import balance_service
    from bot.services.referral.referral_service import referral_service
    
    balance = await balance_service.get_balance(user_id)
    referrals = await referral_service.get_referral_count(user_id)
    username_display = user.get('username') or "yo'q"
    
    text = (
        f"⭐ <b>PREMIUM SO'ROV</b>\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Ism: {user.get('fullname', 'N/A')}\n"
        f"📱 Username: @{username_display}\n"
        f"📞 Telefon: {user.get('phone') or 'berilmagan'}\n"
        f"💎 Balans: {await balance_service.format_balance(balance)}\n"
        f"👥 Referrallar: {referrals}\n\n"
        f"Tasdiqlamoqchimisiz?"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_premium_action_keyboard(user_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("premium_approve:"))
async def approve_premium_request(callback: CallbackQuery):
    """Approve premium request."""
    user_id = int(callback.data.split(":")[1])
    
    success = await premium_service.approve_premium(user_id)
    
    if success:
        await callback.answer("✅ Premium tasdiqlandi!", show_alert=True)
        
        # Notify user
        try:
            user = await user_repo.get_by_id(user_id)
            await callback.bot.send_message(
                user_id,
                "🎉 <b>TABRIKLAYMIZ!</b>\n\n"
                "Premium so'rovingiz qabul qilindi!\n\n"
                "⭐ Endi barcha premium imkoniyatlardan foydalanishingiz mumkin.",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")
        
        # Back to list
        requests = await premium_service.get_pending_requests()
        
        if requests:
            await callback.message.edit_text(
                f"⭐ <b>PREMIUM SO'ROVLAR</b>\n\n"
                f"Jami: {len(requests)} ta\n\n"
                f"Foydalanuvchini tanlang:",
                reply_markup=get_premium_requests_keyboard(requests),
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text(
                "📭 <b>PREMIUM SO'ROVLAR</b>\n\n"
                "Hozircha so'rovlar yo'q.",
                parse_mode="HTML"
            )
    else:
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("premium_reject:"))
async def reject_premium_request(callback: CallbackQuery):
    """Reject premium request."""
    user_id = int(callback.data.split(":")[1])
    
    success = await premium_service.reject_premium(user_id)
    
    if success:
        await callback.answer("✅ So'rov rad etildi!", show_alert=True)
        
        # Notify user
        try:
            await callback.bot.send_message(
                user_id,
                "❌ <b>SO'ROV RAD ETILDI</b>\n\n"
                "Premium so'rovingiz rad etildi.\n\n"
                "Keyinroq qayta urinib ko'ring.",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")
        
        # Back to list
        requests = await premium_service.get_pending_requests()
        
        if requests:
            await callback.message.edit_text(
                f"⭐ <b>PREMIUM SO'ROVLAR</b>\n\n"
                f"Jami: {len(requests)} ta\n\n"
                f"Foydalanuvchini tanlang:",
                reply_markup=get_premium_requests_keyboard(requests),
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text(
                "📭 <b>PREMIUM SO'ROVLAR</b>\n\n"
                "Hozircha so'rovlar yo'q.",
                parse_mode="HTML"
            )
    else:
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)


@router.callback_query(IsAdmin(), F.data == "premium_requests")
async def back_to_premium_requests(callback: CallbackQuery):
    """Back to premium requests list."""
    requests = await premium_service.get_pending_requests()
    
    if not requests:
        await callback.message.edit_text(
            "📭 <b>PREMIUM SO'ROVLAR</b>\n\n"
            "Hozircha so'rovlar yo'q.",
            parse_mode="HTML"
        )
        return
    
    await callback.message.edit_text(
        f"⭐ <b>PREMIUM SO'ROVLAR</b>\n\n"
        f"Jami: {len(requests)} ta\n\n"
        f"Foydalanuvchini tanlang:",
        reply_markup=get_premium_requests_keyboard(requests),
        parse_mode="HTML"
    )
    await callback.answer()
