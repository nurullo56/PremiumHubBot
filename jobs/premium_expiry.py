"""Premium expiry check job."""

import asyncio
import logging
from datetime import datetime

from aiogram import Bot

from bot.database.repositories.premium_repo import premium_repo
from bot.utils.common.timezone import parse_uzbek_datetime

logger = logging.getLogger(__name__)

_expiry_task = None


async def check_expired_premium(bot: Bot):
    """Check and notify expired premium users."""
    try:
        active_users = await premium_repo.get_active()
        now = datetime.now()
        expired_count = 0
        
        for user in active_users:
            expiry_date_str = user.get('premium_expiry')
            
            if not expiry_date_str:
                continue
            
            try:
                expiry_date = parse_uzbek_datetime(expiry_date_str)
                
                if now > expiry_date:
                    await premium_repo.set_status(user['user_id'], 'expired')
                    expired_count += 1
                    
                    try:
                        await bot.send_message(
                            user['user_id'],
                            "⏰ <b>Premium obuna muddati tugadi</b>\n\n"
                            "Premium obunangiz muddati tugadi. Qayta faollashtirish uchun admin bilan bog'laning.",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logger.error(f"Failed to notify user {user['user_id']}: {e}")
                        
            except Exception as e:
                logger.error(f"Error processing user {user['user_id']}: {e}")
        
        if expired_count > 0:
            logger.info(f"✅ Processed {expired_count} expired premium users")
            
    except Exception as e:
        logger.error(f"❌ Premium expiry check error: {e}", exc_info=True)


async def premium_expiry_job(bot: Bot):
    """Main premium expiry check loop (runs daily)."""
    logger.info("🔄 Premium expiry job started")
    
    while True:
        try:
            await asyncio.sleep(86400)
            
            logger.info("⏰ Checking expired premium users...")
            await check_expired_premium(bot)
            
        except asyncio.CancelledError:
            logger.info("⏸️ Premium expiry job cancelled")
            break
        except Exception as e:
            logger.error(f"❌ Premium expiry job error: {e}", exc_info=True)
            await asyncio.sleep(3600)


async def start_premium_expiry_job(bot: Bot):
    """Start the premium expiry background job."""
    global _expiry_task
    
    if _expiry_task and not _expiry_task.done():
        logger.warning("⚠️ Premium expiry job already running")
        return
    
    _expiry_task = asyncio.create_task(premium_expiry_job(bot))
    logger.info("✅ Premium expiry job started")


async def stop_premium_expiry_job():
    """Stop the premium expiry background job."""
    global _expiry_task
    
    if _expiry_task and not _expiry_task.done():
        _expiry_task.cancel()
        try:
            await _expiry_task
        except asyncio.CancelledError:
            pass
        logger.info("✅ Premium expiry job stopped")
