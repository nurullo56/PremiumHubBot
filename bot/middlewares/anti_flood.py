"""Anti-flood middleware - rate limiting."""

import logging
import time
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineQuery

from bot.config.constants import (
    ANTI_FLOOD_DEFAULT_DELAY,
    ANTI_FLOOD_CALLBACK_DELAY,
    ANTI_FLOOD_INLINE_DELAY
)

logger = logging.getLogger(__name__)


class AntiFloodMiddleware(BaseMiddleware):
    """
    Anti-flood middleware with configurable delays for different update types.
    
    Prevents users from spamming the bot with rapid requests.
    """
    
    def __init__(
        self,
        default_delay: float = ANTI_FLOOD_DEFAULT_DELAY,
        callback_delay: float = ANTI_FLOOD_CALLBACK_DELAY,
        inline_delay: float = ANTI_FLOOD_INLINE_DELAY
    ):
        super().__init__()
        self.default_delay = default_delay
        self.callback_delay = callback_delay
        self.inline_delay = inline_delay
        self.user_timestamps: Dict[int, float] = {}
    
    def _get_delay(self, event: Any) -> float:
        """Get appropriate delay based on event type."""
        if isinstance(event, CallbackQuery):
            return self.callback_delay
        elif isinstance(event, InlineQuery):
            return self.inline_delay
        else:
            return self.default_delay
    
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        elif isinstance(event, InlineQuery):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        user_id = user.id
        current_time = time.time()
        delay = self._get_delay(event)
        
        last_time = self.user_timestamps.get(user_id, 0)
        time_passed = current_time - last_time
        
        if time_passed < delay:
            logger.warning(f"⚠️ Anti-flood triggered for user {user_id}")
            
            if isinstance(event, Message):
                await event.answer("⏳ Iltimos, biroz kuting...")
            elif isinstance(event, CallbackQuery):
                await event.answer("⏳ Iltimos, biroz kuting...", show_alert=False)
            
            return None
        
        self.user_timestamps[user_id] = current_time
        
        if len(self.user_timestamps) > 10000:
            cutoff_time = current_time - 3600
            self.user_timestamps = {
                uid: ts for uid, ts in self.user_timestamps.items() 
                if ts > cutoff_time
            }
        
        return await handler(event, data)
