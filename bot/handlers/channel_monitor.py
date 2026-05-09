# bot/handlers/channel_monitor.py
"""
Channel Monitor Handler - HANDLER ONLY
✅ Qisqa, aniq, faqat event handling
✅ Service ni chaqiradi, DB ni emas
✅ No business logic here
"""

import logging
from aiogram import Router, Bot
from aiogram.types import ChatMemberUpdated
from aiogram.filters import IS_NOT_MEMBER, IS_MEMBER, ChatMemberUpdatedFilter

from bot.services.channel.channel_monitor_service import channel_monitor_service
from bot.database.repositories.user_repo import user_repo
from bot.database.repositories.balance_repo import balance_repo
from bot.database.repositories.join_request_repo import JoinRequestRepository
from bot.utils.subscription_checker import subscription_checker
from bot.keyboards.user.main_menu import get_main_keyboard

logger = logging.getLogger(__name__)
router = Router(name="channel_monitor")


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def user_left_channel(event: ChatMemberUpdated, bot: Bot):
    """
    Handle user leaving channel.
    ONLY calls service - NO DB operations here!
    """
    user_id = event.from_user.id
    chat_id = event.chat.id
    chat_title = event.chat.title or "Kanal"
    chat_username = event.chat.username
    
    logger.info(f"🚪 User left: user={user_id}, chat={chat_id}")
    
    # Check if channel is mandatory (via service)
    is_mandatory, channel_name = await channel_monitor_service.is_mandatory_channel(
        chat_id, chat_username
    )
    
    if not is_mandatory:
        logger.debug(f"⏭️ Not mandatory channel: {chat_id}")
        return
    
    logger.warning(f"⚠️ User {user_id} left mandatory channel: {channel_name}")
    
    # Process bonus return (via service)
    # Managed kanaldan chiqqanda join_requests DB ni tozala
    # (subscription fallback check uchun, API ishlamasa ham to'g'ri ko'rsatsin)
    await JoinRequestRepository.clear_request(user_id, str(chat_id))

    result = await channel_monitor_service.process_bonus_return(
        user_id=user_id,
        channel_id=str(chat_id),
        channel_name=channel_name or chat_title,
        bot=bot
    )

    if result.success:
        logger.info(f"✅ Bonus returned: user={user_id}, referrer={result.referrer_id}")
    else:
        logger.debug(f"⏭️ Bonus return skipped: {result.reason}")


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def user_joined_channel(event: ChatMemberUpdated, bot: Bot):
    """
    Handle user joining channel.
    ONLY calls service - NO DB operations here!
    """
    user_id = event.from_user.id
    chat_id = event.chat.id
    chat_username = event.chat.username

    logger.info(f"👋 User joined: user={user_id}, chat={chat_id}")

    is_mandatory, channel_name = await channel_monitor_service.is_mandatory_channel(
        chat_id, chat_username
    )

    if not is_mandatory:
        return

    logger.info(f"✅ User {user_id} joined mandatory channel: {channel_name}")

    await _auto_complete_registration(user_id, bot)
    await _restore_per_channel_bonus(user_id, str(chat_id), channel_name or chat_title, bot)


async def _auto_complete_registration(user_id: int, bot: Bot) -> None:
    """
    Foydalanuvchi kanalga qo'shilganda chaqiriladi.
    Ikki holat uchun ishlaydi:
      1. Yangi user — ro'yxatdan o'tayotgan (phone bor, is_subscribed=False)
      2. Qaytuvchi user — avval chiqib ketgan (is_subscribed=False, referral_bonus_given=0)
    """
    try:
        db_user = await user_repo.get_by_id(user_id)

        # Foydalanuvchi yo'q yoki allaqachon to'liq obuna — hech narsa qilma
        if not db_user or not db_user.get('phone'):
            return
        if db_user.get('is_subscribed'):
            return

        # Hamma kanallarga obuna bo'lganini tekshir
        all_subscribed = await subscription_checker.check_user_subscriptions(bot, user_id)
        if not all_subscribed:
            return

        # Obunani tasdiqlash
        await user_repo.update_subscription(user_id, True)
        logger.info(f"✅ Subscription confirmed: {user_id}")

        # Referral bonus berish (yangi ham, qaytuvchi ham)
        if db_user.get('referred_by') and not db_user.get('referral_bonus_given'):
            try:
                referrer_id = db_user['referred_by']
                referrer = await user_repo.get_by_id(referrer_id)
                if not referrer or referrer.get('is_blocked'):
                    logger.warning(f"⚠️ Referrer unavailable ({referrer_id}) — skipping bonus")
                else:
                    from bot.database.repositories.referral_bonus_repo import give_referral_bonus
                    success, _ = await give_referral_bonus(
                        referrer_id=referrer_id,
                        new_user_id=user_id,
                        fullname=db_user.get('fullname', 'Foydalanuvchi'),
                        bot=bot
                    )
                    if success:
                        logger.info(f"✅ Referral bonus given: {referrer_id} <- {user_id}")
            except Exception as e:
                logger.error(f"❌ Referral bonus error: {e}")

        # Foydalanuvchiga xabar yuborish
        balance = await balance_repo.get_balance(user_id)
        fullname = db_user.get('fullname', 'Foydalanuvchi')
        from bot.config import settings

        await bot.send_message(
            user_id,
            f"✅ <b>Barcha obunalar tasdiqlandi!</b>\n\n"
            f"👋 Xush kelibsiz, {fullname}!\n"
            f"💰 Balansingiz: {float(balance):.2f} 💎\n\n"
            f"🎁 <b>Bonus olish uchun:</b>\n"
            f"\"✨BEPUL PREMIUM OLISH💫\" tugmasini bosing!",
            reply_markup=get_main_keyboard(is_admin=settings.is_admin(user_id)),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"❌ _auto_complete_registration error for {user_id}: {e}", exc_info=True)


async def _restore_per_channel_bonus(user_id: int, channel_id: str, channel_name: str, bot: Bot) -> None:
    """
    User kanalga qaytib kirganda 0.2 olmos bonusni referrerga qaytaradi.
    Faqat shu kanal uchun oldindan ayrilgan bo'lsa ishlaydi.
    """
    try:
        from bot.database.repositories.channel_monitor_repo import channel_monitor_repo
        from bot.services.finance.balance_service import balance_service
        from decimal import Decimal
        from bot.config.constants import CHANNEL_LEAVE_DEDUCTION

        db_user = await user_repo.get_by_id(user_id)
        if not db_user or not db_user.get('referral_bonus_given'):
            return

        referrer_id = db_user.get('referred_by')
        if not referrer_id:
            return

        was_deducted = await channel_monitor_repo.is_channel_bonus_deducted(user_id, channel_id)
        if not was_deducted:
            return

        referrer = await user_repo.get_by_id(referrer_id)
        if not referrer or referrer.get('is_blocked'):
            return

        amount = Decimal(str(CHANNEL_LEAVE_DEDUCTION))
        success, _, new_balance = await balance_service.add_balance(
            user_id=referrer_id,
            amount=amount,
            description=f"+{amount}💎: {db_user.get('fullname', 'User')} «{channel_name}» ga qaytdi",
            transaction_type="bonus_restore"
        )

        if success:
            await channel_monitor_repo.clear_channel_bonus_deducted(user_id, channel_id)
            logger.info(f"✅ Bonus restored: referrer={referrer_id} +{amount} <- user={user_id} channel={channel_id}")
            try:
                await bot.send_message(
                    referrer_id,
                    f"✅ <b>Bonus qaytarildi!</b>\n\n"
                    f"👤 <b>{db_user.get('fullname', 'Foydalanuvchi')}</b> «{channel_name}» ga qaytib kirdi!\n"
                    f"💎 <b>+{amount} olmos</b> qo'shildi.\n"
                    f"💰 Balansingiz: <b>{float(new_balance):.2f} olmos</b>",
                    parse_mode="HTML"
                )
            except Exception:
                pass

    except Exception as e:
        logger.error(f"❌ _restore_per_channel_bonus error for {user_id}: {e}", exc_info=True)


__all__ = ["router"]