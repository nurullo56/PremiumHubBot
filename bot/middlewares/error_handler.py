"""Global error handler middleware - prevents bot crashes."""

import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update, ErrorEvent

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Global error handler that catches all exceptions and prevents bot crashes.
    
    This middleware ensures the bot never stops due to unhandled exceptions.
    All errors are logged and optionally sent to Sentry.
    """
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
            
        except Exception as e:
            logger.error(
                f"❌ Unhandled exception in handler",
                exc_info=True,
                extra={
                    'update': event.model_dump() if hasattr(event, 'model_dump') else str(event),
                    'error_type': type(e).__name__
                }
            )
            
            try:
                from bot.monitoring.sentry import capture_exception
                capture_exception(e)
            except ImportError:
                pass
            
            try:
                if event.message:
                    await event.message.answer(
                        "⚠️ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.\n"
                        "Agar muammo takrorlansa, admin bilan bog'laning."
                    )
                elif event.callback_query:
                    await event.callback_query.answer(
                        "⚠️ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
                        show_alert=True
                    )
            except Exception as notify_error:
                logger.error(f"Failed to notify user about error: {notify_error}")
            
            return None


async def setup_error_handler(dp):
    """Setup global error handler for all update types."""
    
    @dp.errors()
    async def error_handler(event: ErrorEvent):
        """Handle errors from error events."""
        logger.error(
            f"❌ Error event caught: {event.exception}",
            exc_info=event.exception
        )
        
        try:
            from bot.monitoring.sentry import capture_exception
            capture_exception(event.exception)
        except ImportError:
            pass
        
        return True
