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

ALLOWED_UPDATES = ["message", "callback_query", "chat_member", "chat_join_request"]

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

    if settings.use_webhook:
        await bot.set_webhook(
            url=settings.webhook_url,
            allowed_updates=ALLOWED_UPDATES,
            drop_pending_updates=True,
        )
        logger.info(f"🔗 Webhook set: {settings.webhook_url}")

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

    if settings.use_webhook:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("🔗 Webhook deleted")

    await optimize_database()
    await bot.session.close()

    logger.info("✅ Shutdown complete")


def handle_signal(sig):
    """Handle shutdown signals."""
    logger.info(f"⚠️ Received signal {sig.name}, initiating graceful shutdown...")
    shutdown_event.set()


def _build_dispatcher() -> tuple[Bot, Dispatcher]:
    """Create and configure bot + dispatcher."""
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    from bot.utils.bot.instance import BotInstance
    BotInstance.set(bot)

    dp = Dispatcher()
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())
    dp.message.middleware(AntiFloodMiddleware())
    dp.callback_query.middleware(AntiFloodMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    return bot, dp


async def _run_polling(bot: Bot, dp: Dispatcher) -> None:
    """Run bot in long-polling mode."""
    loop = asyncio.get_event_loop()

    if sys.platform != 'win32':
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
    else:
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda s, f: handle_signal(s))

    polling_task = asyncio.create_task(
        dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)
    )
    logger.info("✅ Bot started polling")

    await shutdown_event.wait()

    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass


async def _run_webhook(bot: Bot, dp: Dispatcher) -> None:
    """Run bot in webhook mode using aiohttp."""
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    app = web.Application()

    # Webhook handler
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path=settings.webhook_path)

    setup_application(app, dp, bot=bot)

    # Static fayl serveri — web/ papkasini serve qiladi
    web_dir = Path(__file__).parent.parent / "web"
    if web_dir.exists():
        app.router.add_static("/captcha", web_dir / "captcha", show_index=False)
        logger.info(f"📁 Static served: /captcha → {web_dir / 'captcha'}")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=settings.webapp_host, port=settings.webapp_port)
    await site.start()

    logger.info(f"✅ Webhook server started on {settings.webapp_host}:{settings.webapp_port}")
    logger.info(f"🔗 Webhook path: {settings.webhook_path}")
    logger.info(f"🌐 Captcha URL:  {settings.webhook_host}/captcha/index.html")

    # Keep running until shutdown signal
    loop = asyncio.get_event_loop()
    if sys.platform != 'win32':
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
    else:
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda s, f: handle_signal(s))

    await shutdown_event.wait()
    await runner.cleanup()


async def main():
    """Main bot execution."""
    global bot_instance, dispatcher_instance

    try:
        logger.info("📦 Initializing bot...")

        init_sentry(settings.sentry_dsn, settings.environment)
        await init_database()

        from bot.database.migrations import run_migrations
        await run_migrations()

        bot_instance, dispatcher_instance = _build_dispatcher()

        await setup_error_handler(dispatcher_instance)

        main_router = get_main_router()
        dispatcher_instance.include_router(main_router)

        logger.info("✅ Handlers registered")
        logger.info("✅ Bot initialized")

        await on_startup(bot_instance)

        if settings.use_webhook:
            await _run_webhook(bot_instance, dispatcher_instance)
        else:
            await _run_polling(bot_instance, dispatcher_instance)

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
