# bot/utils/common/bot_commands.py
"""Bot commands setup for Telegram menu."""

import logging
from typing import List
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from bot.config import settings

logger = logging.getLogger(__name__)


# ===================== KOMANDALAR RO'YXATI =====================

DEFAULT_COMMANDS: List[BotCommand] = [
    BotCommand(command="start", description="🚀 Botni ishga tushirish"),
    BotCommand(command="admin", description="👮‍♂️ Admin panel (faqat admin)"),
    BotCommand(command="cancel", description="❌ Jarayonni bekor qilish"),
]

USER_COMMANDS: List[BotCommand] = [
    BotCommand(command="start", description="🚀 Botni ishga tushirish"),
    BotCommand(command="cancel", description="❌ Jarayonni bekor qilish"),
]

ADMIN_COMMANDS: List[BotCommand] = [
    BotCommand(command="start", description="🚀 Botni ishga tushirish"),
    BotCommand(command="admin", description="👮‍♂️ Admin panel"),
    BotCommand(command="users", description="👥 Foydalanuvchilar ro'yxati"),
    BotCommand(command="user", description="👤 Foydalanuvchi ma'lumotlari"),
    BotCommand(command="search_user", description="🔍 Foydalanuvchi qidirish"),
    BotCommand(command="cancel", description="❌ Jarayonni bekor qilish"),
    BotCommand(command="test55", description="🧪 Test: 55 referral + 100 balance"),
    BotCommand(command="testgive", description="🧪 Test: Give referrals and balance"),
    BotCommand(command="testreset", description="🧪 Test: Reset premium"),
    BotCommand(command="testinfo", description="🧪 Test: User info"),
    BotCommand(command="testhelp", description="🧪 Test: Help"),
]


async def set_bot_commands(bot: Bot) -> bool:
    """
    Set bot commands for Telegram menu.
    
    Args:
        bot: Bot instance
    
    Returns:
        bool: True if successful
    """
    try:
        # Set default commands for all users
        await bot.set_my_commands(
            commands=DEFAULT_COMMANDS,
            scope=BotCommandScopeDefault()
        )
        
        logger.info(f"✅ Bot commands set successfully")
        logger.info(f"📋 Commands: {[c.command for c in DEFAULT_COMMANDS]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to set bot commands: {e}")
        return False


async def set_admin_commands(bot: Bot, admin_id: int) -> bool:
    """
    Set admin-specific commands for a specific admin.
    
    Args:
        bot: Bot instance
        admin_id: Admin user ID
    
    Returns:
        bool: True if successful
    """
    try:
        from aiogram.types import BotCommandScopeChat
        
        await bot.set_my_commands(
            commands=ADMIN_COMMANDS,
            scope=BotCommandScopeChat(chat_id=admin_id)
        )
        
        logger.info(f"✅ Admin commands set for {admin_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to set admin commands for {admin_id}: {e}")
        return False


async def setup_all_commands(bot: Bot) -> None:
    """
    Setup all commands for bot and admins.
    
    Args:
        bot: Bot instance
    """
    # Set default commands
    await set_bot_commands(bot)
    
    # Set admin commands for each admin
    for admin_id in settings.admin_ids:
        await set_admin_commands(bot, admin_id)
    
    logger.info("✅ All commands setup complete")


__all__ = [
    "DEFAULT_COMMANDS",
    "USER_COMMANDS",
    "ADMIN_COMMANDS",
    "set_bot_commands",
    "set_admin_commands",
    "setup_all_commands"
]