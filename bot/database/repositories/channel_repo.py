"""Channel repository - database access only."""

import logging
from typing import List, Dict, Any, Optional

from bot.database.base import get_db

logger = logging.getLogger(__name__)


class ChannelRepository:
    
    @staticmethod
    async def create(
        channel_id: str,
        channel_name: str,
        channel_url: str,
        added_by: Optional[int] = None,
        description: Optional[str] = None,
        created_at: str = None
    ) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""   
                    INSERT INTO channels (channel_id, channel_name, channel_url, added_by, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(channel_id) DO UPDATE SET
                        channel_name = excluded.channel_name,
                        channel_url = excluded.channel_url,
                        description = excluded.description
                """, (channel_id, channel_name, channel_url, added_by, description, created_at))
                await db.commit()
                logger.info(f"✅ Channel created/updated: {channel_name}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create channel {channel_id}: {e}")
            return False
    
    @staticmethod
    async def get_by_id(channel_id: str) -> Optional[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT * FROM channels WHERE channel_id = ?", (channel_id,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get channel {channel_id}: {e}")
            return None
    
    @staticmethod
    async def get_all_active() -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT * FROM channels WHERE is_active = 1 ORDER BY created_at DESC"
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get active channels: {e}")
            return []
    
    @staticmethod
    async def get_all() -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT * FROM channels ORDER BY created_at DESC")
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get all channels: {e}")
            return []
    
    @staticmethod
    async def activate(channel_id: str) -> bool:
        try:
            async with get_db() as db:
                await db.execute("UPDATE channels SET is_active = 1 WHERE channel_id = ?", (channel_id,))
                await db.commit()
                logger.info(f"✅ Channel activated: {channel_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to activate channel {channel_id}: {e}")
            return False
    
    @staticmethod
    async def deactivate(channel_id: str) -> bool:
        try:
            async with get_db() as db:
                await db.execute("UPDATE channels SET is_active = 0 WHERE channel_id = ?", (channel_id,))
                await db.commit()
                logger.info(f"✅ Channel deactivated: {channel_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to deactivate channel {channel_id}: {e}")
            return False
    
    @staticmethod
    async def delete(channel_id: str) -> bool:
        try:
            async with get_db() as db:
                await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
                await db.commit()
                logger.info(f"✅ Channel deleted: {channel_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to delete channel {channel_id}: {e}")
            return False
    
    @staticmethod
    async def get_count() -> int:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT COUNT(*) as count FROM channels WHERE is_active = 1")
                result = await cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Failed to get channel count: {e}")
            return 0


channel_repo = ChannelRepository()