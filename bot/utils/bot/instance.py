# bot/utils/bot/_instance.py
"""Global bot instance manager for accessing bot from anywhere."""

import logging
from typing import Optional
from aiogram import Bot

logger = logging.getLogger(__name__)


class BotInstance:
    """Singleton wrapper for bot instance."""
    
    _instance: Optional[Bot] = None
    _bot: Optional[Bot] = None
    
    @classmethod
    def set(cls, bot: Bot) -> None:
        """Set bot instance."""
        cls._bot = bot
        cls._instance = cls
        logger.info("✅ Bot instance set")
    
    @classmethod
    def get(cls) -> Bot:
        """Get bot instance."""
        if cls._bot is None:
            raise RuntimeError("Bot instance not set! Call BotInstance.set() first")
        return cls._bot
    
    @classmethod
    def is_ready(cls) -> bool:
        """Check if bot instance is ready."""
        return cls._bot is not None


# Global instance for easy import
bot_instance = BotInstance()


__all__ = ["BotInstance", "bot_instance"]