"""Logging middleware - logs all incoming updates."""

import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """
    Logging middleware to track all incoming updates.
    
    Logs user interactions for debugging and analytics.
    """
    
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            user = event.from_user
            text = event.text or event.caption or "[media]"
            
            logger.info(
                f"📨 Message from {user.id} (@{user.username}): {text[:50]}"
            )
            
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            callback_data = event.data
            
            logger.info(
                f"🔘 Callback from {user.id} (@{user.username}): {callback_data}"
            )
        
        return await handler(event, data)
