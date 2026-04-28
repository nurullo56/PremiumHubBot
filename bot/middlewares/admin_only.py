"""Admin-only middleware - restricts access to admin handlers."""

import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot.config import settings

logger = logging.getLogger(__name__)


class AdminOnlyMiddleware(BaseMiddleware):
    """
    Middleware to restrict access to admin-only handlers.
    
    Apply this to admin routers to ensure only admins can access them.
    """
    
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
        
        if not user:
            return None
        
        if not settings.is_admin(user.id):
            logger.warning(f"⚠️ Non-admin user {user.id} attempted to access admin handler")
            
            if isinstance(event, Message):
                await event.answer("❌ Bu funksiya faqat adminlar uchun!")
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ Bu funksiya faqat adminlar uchun!", show_alert=True)
            
            return None
        
        return await handler(event, data)
