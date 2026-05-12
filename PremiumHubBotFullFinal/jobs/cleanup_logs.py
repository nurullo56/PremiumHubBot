"""Log cleanup job."""

import asyncio
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

_cleanup_task = None

LOG_RETENTION_DAYS = 30


async def cleanup_old_logs():
    """Delete log files older than retention period."""
    log_dir = Path("logs")
    
    if not log_dir.exists():
        return
    
    cutoff_time = datetime.now().timestamp() - (LOG_RETENTION_DAYS * 86400)
    deleted_count = 0
    
    for log_file in log_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff_time:
            log_file.unlink()
            deleted_count += 1
            logger.info(f"🗑️ Deleted old log: {log_file.name}")
    
    if deleted_count > 0:
        logger.info(f"✅ Cleaned up {deleted_count} old log files")


async def cleanup_job():
    """Main cleanup job loop (runs daily)."""
    logger.info("🔄 Cleanup job started")
    
    while True:
        try:
            await asyncio.sleep(86400)
            
            logger.info("🧹 Cleaning up old logs...")
            await cleanup_old_logs()
            
        except asyncio.CancelledError:
            logger.info("⏸️ Cleanup job cancelled")
            break
        except Exception as e:
            logger.error(f"❌ Cleanup job error: {e}", exc_info=True)
            await asyncio.sleep(3600)


async def start_cleanup_job():
    """Start the cleanup background job."""
    global _cleanup_task
    
    if _cleanup_task and not _cleanup_task.done():
        logger.warning("⚠️ Cleanup job already running")
        return
    
    _cleanup_task = asyncio.create_task(cleanup_job())
    logger.info("✅ Cleanup job started")


async def stop_cleanup_job():
    """Stop the cleanup background job."""
    global _cleanup_task
    
    if _cleanup_task and not _cleanup_task.done():
        _cleanup_task.cancel()
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            pass
        logger.info("✅ Cleanup job stopped")
