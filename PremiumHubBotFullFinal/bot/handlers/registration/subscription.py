# bot/handlers/registration/subscription.py
"""Subscription check handler."""

import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.database.repositories.user_repo import user_repo
from bot.utils.subscription_checker import subscription_checker
from bot.keyboards.user.main_menu import get_main_keyboard
from bot.states.user.registration import RegistrationStates

logger = logging.getLogger(__name__)
router = Router(name="registration_subscription")


async def check_subscription(user_id: int, message: Message, bot: Bot) -> bool:
    """
    Check if user subscribed to all mandatory channels.
    Uses new subscription_checker utility.
    """
    logger.info(f"📺 Subscription check: user_id={user_id}")
    
    # Use utility for checking
    keyboard = await subscription_checker.get_subscription_keyboard(bot, user_id)
    
    if keyboard:
        # User needs to subscribe
        logger.info(f"⏳ Subscription needed: {user_id}")
        await message.answer(
            "⚠️ <b>Obuna bo'lish talab qilinadi</b>\n\n"
            "Botdan to'liq foydalanish uchun quyidagi kanal va guruhlarga obuna bo'ling:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return False
    
    # All subscribed
    logger.info(f"✅ All subscribed: {user_id}")
    await user_repo.update_subscription(user_id, True)
    return True


async def ask_subscription(message: Message, state: FSMContext):
    """Show mandatory channel subscription prompt to the user."""
    user_id = message.from_user.id
    bot = message.bot

    keyboard = await subscription_checker.get_subscription_keyboard(bot, user_id)

    if not keyboard:
        # No mandatory channels or already subscribed — mark and skip this step
        await user_repo.update_subscription(user_id, True)
        return

    await message.answer(
        "⚠️ <b>Obuna bo'lish talab qilinadi</b>\n\n"
        "Botdan to'liq foydalanish uchun quyidagi kanal va guruhlarga obuna bo'ling:\n\n"
        "✅ Obuna bo'lganingizdan so'ng \"Tekshirish\" tugmasini bosing.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_subscription)


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Check subscription callback - uses new utility."""
    user_id = callback.from_user.id

    await callback.answer("🔄 Tekshirilmoqda...", show_alert=False)

    is_subscribed = await subscription_checker.check_user_subscriptions(bot, user_id)

    if is_subscribed:
        await user_repo.update_subscription(user_id, True)
        await callback.message.delete()

        await callback.message.answer(
            "✅ <b>Barcha obunalar tasdiqlandi!</b>\n\n"
            "Endi botdan to'liq foydalanishingiz mumkin.\n\n"
            "🎁 <b>Bonus olish uchun:</b>\n"
            "1️⃣ \"✨BEPUL PREMIUM OLISH💫\" tugmasini bosing\n"
            "2️⃣ Do'stlaringizni taklif qiling\n"
            "3️⃣ Har bir do'st uchun <b>1.4 olmos</b> oling!\n"
            "4️⃣ 40 ta do'st uchun <b>BEPUL Telegram Premium</b>!",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()

        # Referral bonus: give immediately on registration completion
        user = await user_repo.get_by_id(user_id)
        if user and user.get('referred_by') and not user.get('referral_bonus_given'):
            try:
                from bot.database.repositories.referral_bonus_repo import give_referral_bonus
                success, msg = await give_referral_bonus(
                    referrer_id=user['referred_by'],
                    new_user_id=user_id,
                    fullname=callback.from_user.full_name,
                    bot=bot
                )
                if success:
                    logger.info(f"✅ Referral bonus given: {user['referred_by']} <- {user_id}")
                else:
                    logger.warning(f"⚠️ Referral bonus skipped: {msg}")
            except Exception as e:
                logger.error(f"❌ Referral bonus error on registration: {e}", exc_info=True)
    else:
        await callback.answer(
            "❌ Hali barcha kanallarga obuna bo'lmadingiz!",
            show_alert=True
        )
        
        # Get updated keyboard with unsubscribed channels
        keyboard = await subscription_checker.get_subscription_keyboard(bot, user_id)
        if keyboard:
            try:
                await callback.message.edit_reply_markup(reply_markup=keyboard)
            except:
                pass


__all__ = ["router", "check_subscription", "ask_subscription", "check_subscription_callback"]