"""Premium repository - database access only."""

import logging
from typing import List, Dict, Any, Optional

from bot.database.base import get_db

logger = logging.getLogger(__name__)


class PremiumRepository:
    
    @staticmethod
    async def get_status(user_id: int) -> Optional[str]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT premium_status FROM users WHERE user_id = ?", (user_id,)
                )
                result = await cursor.fetchone()
                return result['premium_status'] if result else None
        except Exception as e:
            logger.error(f"❌ Failed to get premium status for {user_id}: {e}")
            return None
    
    @staticmethod
    async def set_status(user_id: int, status: str, expiry: Optional[str] = None) -> bool:
        try:
            async with get_db() as db:
                await db.execute(
                    "UPDATE users SET premium_status = ?, premium_expiry = ? WHERE user_id = ?",
                    (status, expiry, user_id)
                )
                await db.commit()
                logger.info(f"✅ Premium status updated for {user_id}: {status}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to set premium status for {user_id}: {e}")
            return False
    
    @staticmethod
    async def mark_admin_notified(user_id: int) -> bool:
        try:
            async with get_db() as db:
                await db.execute(
                    "UPDATE users SET admin_notified = 1 WHERE user_id = ?", (user_id,)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to mark admin notified for {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_pending() -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT * FROM users WHERE premium_status = 'pending' ORDER BY registration_date DESC"
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get pending premium users: {e}")
            return []
    
    @staticmethod
    async def get_active() -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT * FROM users WHERE premium_status = 'approved' OR premium_status = 'active'"
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get active premium users: {e}")
            return []
    
    @staticmethod
    async def get_count_by_status(status: str) -> int:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM users WHERE premium_status = ?", (status,)
                )
                result = await cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Failed to get premium count for status {status}: {e}")
            return 0


premium_repo = PremiumRepository()
