"""Automatic database backup job."""

import asyncio
import logging
import shutil
from pathlib import Path
from datetime import datetime

from aiogram import Bot

from bot.config import settings
from bot.config.constants import BACKUP_INTERVAL_HOURS, BACKUP_RETENTION_DAYS

logger = logging.getLogger(__name__)

_backup_task = None


async def create_backup() -> Path:
    """
    Create database backup.
    
    Returns:
        Path: Path to backup file
    """
    db_path = Path(settings.db_path)
    
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"backup_{timestamp}.db"
    
    shutil.copy2(db_path, backup_path)
    
    logger.info(f"✅ Database backup created: {backup_path}")
    
    return backup_path


async def cleanup_old_backups():
    """Delete backups older than retention days."""
    backup_dir = Path("backups")
    
    if not backup_dir.exists():
        return
    
    cutoff_time = datetime.now().timestamp() - (BACKUP_RETENTION_DAYS * 86400)
    deleted_count = 0
    
    for backup_file in backup_dir.glob("backup_*.db"):
        if backup_file.stat().st_mtime < cutoff_time:
            backup_file.unlink()
            deleted_count += 1
            logger.info(f"🗑️ Deleted old backup: {backup_file.name}")
    
    if deleted_count > 0:
        logger.info(f"✅ Cleaned up {deleted_count} old backups")


async def send_backup_to_admins(bot: Bot, backup_path: Path):
    """Send backup file to all admins."""
    for admin_id in settings.admin_ids:
        try:
            with open(backup_path, 'rb') as backup_file:
                await bot.send_document(
                    admin_id,
                    backup_file,
                    caption=f"📦 Database backup\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            logger.info(f"✅ Backup sent to admin {admin_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send backup to admin {admin_id}: {e}")


async def backup_job(bot: Bot):
    """Main backup job loop."""
    logger.info("🔄 Auto-backup job started")
    
    while True:
        try:
            await asyncio.sleep(BACKUP_INTERVAL_HOURS * 3600)
            
            logger.info("📦 Creating database backup...")
            
            backup_path = await create_backup()
            
            await send_backup_to_admins(bot, backup_path)
            
            await cleanup_old_backups()
            
            logger.info("✅ Backup job completed successfully")
            
        except asyncio.CancelledError:
            logger.info("⏸️ Backup job cancelled")
            break
        except Exception as e:
            logger.error(f"❌ Backup job error: {e}", exc_info=True)
            await asyncio.sleep(3600)


async def start_backup_job(bot: Bot):
    """Start the backup background job."""
    global _backup_task
    
    if _backup_task and not _backup_task.done():
        logger.warning("⚠️ Backup job already running")
        return
    
    _backup_task = asyncio.create_task(backup_job(bot))
    logger.info("✅ Backup job started")


async def stop_backup_job():
    """Stop the backup background job."""
    global _backup_task
    
    if _backup_task and not _backup_task.done():
        _backup_task.cancel()
        try:
            await _backup_task
        except asyncio.CancelledError:
            pass
        logger.info("✅ Backup job stopped")
