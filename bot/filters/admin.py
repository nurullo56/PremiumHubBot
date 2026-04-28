"""Admin filter for checking admin access."""

from typing import Union
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery

from bot.config import settings


class IsAdmin(Filter):
    """
    Filter to check if user is admin.
    
    Usage:
        @router.message(IsAdmin(), F.text == "📊 Statistika")
        async def stats_handler(message: Message):
            ...
    """
    
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        """Check if user is admin."""
        user = event.from_user
        return user.id in settings.admin_ids


__all__ = ["IsAdmin"]
