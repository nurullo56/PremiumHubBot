# bot/utils/common/admin_notify.py
"""Admin notification utilities."""

import logging
from typing import List, Optional
from aiogram import Bot

from bot.config import settings
from bot.utils.common.bot_instance import bot_instance

logger = logging.getLogger(__name__)


async def notify_admin(
    message: str,
    parse_mode: str = "HTML",
    bot: Optional[Bot] = None,
    admin_id: Optional[int] = None
) -> bool:
    """
    Send notification to a specific admin.
    
    Args:
        message: Message text
        parse_mode: Parse mode (HTML/Markdown)
        bot: Bot instance (optional)
        admin_id: Specific admin ID (optional)
    
    Returns:
        bool: True if sent successfully
    """
    try:
        if bot is None:
            bot = bot_instance.get()
        
        target_admin = admin_id or settings.admin_ids[0] if settings.admin_ids else None
        
        if not target_admin:
            logger.warning("⚠️ No admin ID available")
            return False
        
        await bot.send_message(
            chat_id=target_admin,
            text=message,
            parse_mode=parse_mode
        )
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to notify admin: {e}")
        return False


async def notify_all_admins(
    message: str,
    parse_mode: str = "HTML",
    bot: Optional[Bot] = None
) -> List[int]:
    """
    Send notification to all admins.
    
    Args:
        message: Message text
        parse_mode: Parse mode
        bot: Bot instance (optional)
    
    Returns:
        List[int]: List of admin IDs that received the message
    """
    sent_to = []
    
    try:
        if bot is None:
            bot = bot_instance.get()
        
        for admin_id in settings.admin_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=message,
                    parse_mode=parse_mode
                )
                sent_to.append(admin_id)
            except Exception as e:
                logger.error(f"❌ Failed to notify admin {admin_id}: {e}")
        
        return sent_to
        
    except Exception as e:
        logger.error(f"❌ Failed to notify admins: {e}")
        return sent_to


async def notify_new_user(user_id: int, fullname: str, username: Optional[str] = None) -> bool:
    """
    Notify admins about new user registration.
    
    Args:
        user_id: New user ID
        fullname: User full name
        username: User username
    
    Returns:
        bool: True if sent successfully
    """
    username_str = f"@{username}" if username else "❌"
    
    message = (
        f"🆕 <b>YANGI FOYDALANUVCHI!</b>\n\n"
        f"👤 Ism: {fullname}\n"
        f"📱 Username: {username_str}\n"
        f"🆔 ID: <code>{user_id}</code>"
    )
    
    return await notify_all_admins(message)


async def notify_premium_request(user_id: int, fullname: str, username: Optional[str] = None) -> bool:
    """
    Notify admins about premium request.
    
    Args:
        user_id: User ID
        fullname: User full name
        username: User username
    
    Returns:
        bool: True if sent successfully
    """
    username_str = f"@{username}" if username else "❌"
    
    message = (
        f"⭐ <b>PREMIUM SO'ROV!</b>\n\n"
        f"👤 Ism: {fullname}\n"
        f"📱 Username: {username_str}\n"
        f"🆔 ID: <code>{user_id}</code>"
    )
    
    return await notify_all_admins(message)


async def notify_error(error: Exception, context: str = "") -> bool:
    """
    Notify admins about critical error.
    
    Args:
        error: Exception object
        context: Additional context
    
    Returns:
        bool: True if sent successfully
    """
    message = (
        f"🚨 <b>KRITIK XATOLIK!</b>\n\n"
        f"📋 Kontekst: {context}\n"
        f"❌ Xatolik: {type(error).__name__}\n"
        f"📝 Tafsilot: {str(error)[:200]}"
    )
    
    return await notify_all_admins(message)


__all__ = [
    "notify_admin",
    "notify_all_admins",
    "notify_new_user",
    "notify_premium_request",
    "notify_error"
]