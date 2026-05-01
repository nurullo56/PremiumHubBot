"""Main entry point for PremiumHubBot."""
# bot/main.py
import asyncio
import logging
import signal
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.database.base import init_database, optimize_database
from bot.middlewares import (
    ErrorHandlerMiddleware,
    AntiFloodMiddleware,
    LoggingMiddleware
)
from bot.middlewares.error_handler import setup_error_handler
from bot.monitoring import init_sentry
from bot.handlers import get_main_router

# Create necessary directories
Path("logs").mkdir(exist_ok=True)
Path("database").mkdir(exist_ok=True)
Path("backups").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/bot.log', encoding='utf-8')
    ]
)

# Set UTF-8 encoding for console output (Windows fix)
if sys.platform == 'win32':
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)

bot_instance: Bot = None
dispatcher_instance: Dispatcher = None
shutdown_event = asyncio.Event()


async def on_startup(bot: Bot):
    """Execute on bot startup."""
    logger.info("🚀 Bot starting up...")
    
    logger.info(f"Bot: @{(await bot.me()).username}")
    logger.info(f"Admins: {settings.admin_ids}")
    
    # Setup bot commands
    from bot.utils.bot.commands import setup_all_commands
    await setup_all_commands(bot)
    
    from jobs.auto_backup import start_backup_job
    from jobs.premium_expiry import start_premium_expiry_job
    from jobs.cleanup_logs import start_cleanup_job
    
    await start_backup_job(bot)
    await start_premium_expiry_job(bot)
    await start_cleanup_job()
    
    logger.info("✅ Startup complete")


async def on_shutdown(bot: Bot):
    """Execute on bot shutdown."""
    logger.info("🛑 Bot shutting down...")
    
    from jobs.auto_backup import stop_backup_job
    from jobs.premium_expiry import stop_premium_expiry_job
    from jobs.cleanup_logs import stop_cleanup_job
    
    await stop_backup_job()
    await stop_premium_expiry_job()
    await stop_cleanup_job()
    
    await optimize_database()
    
    await bot.session.close()
    
    logger.info("✅ Shutdown complete")


def handle_signal(sig):
    """Handle shutdown signals."""
    logger.info(f"⚠️ Received signal {sig.name}, initiating graceful shutdown...")
    shutdown_event.set()


async def main():
    """Main bot execution."""
    global bot_instance, dispatcher_instance
    
    try:
        logger.info("📦 Initializing bot...")
        
        init_sentry(settings.sentry_dsn, settings.environment)
        
        await init_database()
        
        bot_instance = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Set global bot instance
        from bot.utils.bot.instance import BotInstance
        BotInstance.set(bot_instance)
        
        dispatcher_instance = Dispatcher()
        
        dispatcher_instance.message.middleware(ErrorHandlerMiddleware())
        dispatcher_instance.callback_query.middleware(ErrorHandlerMiddleware())
        
        dispatcher_instance.message.middleware(AntiFloodMiddleware())
        dispatcher_instance.callback_query.middleware(AntiFloodMiddleware())
        
        dispatcher_instance.message.middleware(LoggingMiddleware())
        dispatcher_instance.callback_query.middleware(LoggingMiddleware())
        
        await setup_error_handler(dispatcher_instance)
        
        # Register all handlers
        main_router = get_main_router()
        dispatcher_instance.include_router(main_router)
        
        logger.info("✅ Handlers registered")
        logger.info("✅ Bot initialized")
        
        await on_startup(bot_instance)
        
        loop = asyncio.get_event_loop()
        
        # Signal handlers (Linux only, Windows doesn't support add_signal_handler)
        if sys.platform != 'win32':
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
        else:
            # Windows: use signal.signal instead
            for sig in (signal.SIGTERM, signal.SIGINT):
                signal.signal(sig, lambda s, f: handle_signal(s))
        
        polling_task = asyncio.create_task(
            dispatcher_instance.start_polling(
                bot_instance,
                allowed_updates=["message", "callback_query", "chat_member", "chat_join_request"]
            )
        )
        
        logger.info("✅ Bot started polling")
        
        await shutdown_event.wait()
        
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass
        
        await on_shutdown(bot_instance)
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
