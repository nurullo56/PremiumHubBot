# bot/database/repositories/channel_monitor_repo.py
"""
Channel monitor repository - DATABASE ACCESS ONLY
No business logic here!
"""

import logging
from typing import Optional, Dict, Any, List

from bot.database.base import get_db
from bot.utils.common.timezone import get_uzbek_time

logger = logging.getLogger(__name__)


class ChannelMonitorRepository:
    """Repository for channel monitor database operations."""
    
    @staticmethod
    async def get_mandatory_channels() -> List[Dict[str, Any]]:
        """Get all active mandatory channels."""
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT channel_id, channel_name, channel_url, is_active
                    FROM channels 
                    WHERE is_active = 1
                """)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ get_mandatory_channels error: {e}")
            return []
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT user_id, fullname, referred_by, referral_bonus_given FROM users WHERE user_id = ?",
                    (user_id,)
                )
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ get_user_by_id error: {e}")
            return None
    
    @staticmethod
    async def get_referrer_balance(referrer_id: int) -> Optional[int]:
        """Get referrer's balance (scaled)."""
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT balance_scaled FROM users WHERE user_id = ?",
                    (referrer_id,)
                )
                row = await cursor.fetchone()
                return row['balance_scaled'] if row else None
        except Exception as e:
            logger.error(f"❌ get_referrer_balance error: {e}")
            return None
    
    @staticmethod
    async def update_referrer_balance(referrer_id: int, new_balance_scaled: int) -> bool:
        """Update referrer's balance."""
        try:
            async with get_db() as db:
                await db.execute("""
                    UPDATE users SET balance_scaled = ?
                    WHERE user_id = ?
                """, (new_balance_scaled, referrer_id))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ update_referrer_balance error: {e}")
            return False
    
    @staticmethod
    async def add_balance_history(
        user_id: int,
        amount_scaled: int,
        description: str,
        new_balance_scaled: int,
        transaction_type: str,
        timestamp: str,
        source_user_id: Optional[int] = None
    ) -> bool:
        """Add balance history record."""
        try:
            async with get_db() as db:
                await db.execute("""
                    INSERT INTO balance_history (
                        user_id, amount_scaled, description, 
                        new_balance_scaled, transaction_type, timestamp,
                        source_user_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, amount_scaled, description, new_balance_scaled, 
                      transaction_type, timestamp, source_user_id))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ add_balance_history error: {e}")
            return False
    
    @staticmethod
    async def reset_user_bonus_flag(user_id: int) -> bool:
        """Reset user's referral bonus flag."""
        try:
            async with get_db() as db:
                await db.execute("""
                    UPDATE users SET referral_bonus_given = 0
                    WHERE user_id = ?
                """, (user_id,))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ reset_user_bonus_flag error: {e}")
            return False
    
    @staticmethod
    async def log_channel_leave(
        user_id: int,
        channel_id: str,
        channel_name: str,
        referrer_id: Optional[int],
        bonus_returned: int,
        returned_at: str
    ) -> bool:
        """Log channel leave event."""
        try:
            async with get_db() as db:
                await db.execute("""
                    INSERT INTO channel_leave_logs (
                        user_id, channel_id, channel_name, referrer_id, 
                        bonus_returned, returned_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, channel_id, channel_name, referrer_id, 
                      bonus_returned, returned_at))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ log_channel_leave error: {e}")
            return False
    
    @staticmethod
    async def get_today_bonus_returns_count(referrer_id: int) -> int:
        """Get today's bonus returns count for a referrer."""
        try:
            today_start = get_uzbek_time().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT COUNT(*) as count
                    FROM channel_leave_logs
                    WHERE referrer_id = ? AND bonus_returned = 1 AND returned_at >= ?
                """, (referrer_id, today_start))
                row = await cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"❌ get_today_bonus_returns_count error: {e}")
            return 0


# Singleton
channel_monitor_repo = ChannelMonitorRepository()


__all__ = ["channel_monitor_repo", "ChannelMonitorRepository"]