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
    chat_title = event.chat.title or "Kanal"
    chat_username = event.chat.username
    
    logger.info(f"👋 User joined: user={user_id}, chat={chat_id}")
    
    # Check if channel is mandatory (via service)
    is_mandatory, channel_name = await channel_monitor_service.is_mandatory_channel(
        chat_id, chat_username
    )
    
    if not is_mandatory:
        return
    
    logger.info(f"✅ User {user_id} joined mandatory channel: {channel_name}")
    
    # Send welcome message (via bot directly - no DB needed)
    try:
        await bot.send_message(
            user_id,
            f"👋 <b>Xush kelibsiz!</b>\n\n"
            f"Siz <b>{channel_name}</b> kanaliga qo'shildingiz.\n\n"
            f"💡 Kanalda qolish orqali bonuslaringizni saqlab qolasiz!",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Failed to send welcome message: {e}")


__all__ = ["router"]