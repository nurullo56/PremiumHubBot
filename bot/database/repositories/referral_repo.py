"""Referral repository - database access only."""

import logging
from typing import List, Dict, Any, Optional

from bot.database.base import get_db

logger = logging.getLogger(__name__)


class ReferralRepository:
    
    @staticmethod
    async def get_referrer(user_id: int) -> Optional[int]:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT referred_by FROM users WHERE user_id = ?", (user_id,))
                result = await cursor.fetchone()
                return result['referred_by'] if result else None
        except Exception as e:
            logger.error(f"❌ Failed to get referrer for {user_id}: {e}")
            return None
    
    @staticmethod
    async def get_referral_count(user_id: int) -> int:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM users WHERE referred_by = ?", (user_id,)
                )
                result = await cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Failed to get referral count for {user_id}: {e}")
            return 0
    
    @staticmethod
    async def get_referred_users(user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT user_id, username, fullname, registration_date 
                    FROM users 
                    WHERE referred_by = ? 
                    ORDER BY registration_date DESC 
                    LIMIT ?
                """, (user_id, limit))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get referred users for {user_id}: {e}")
            return []
    
    @staticmethod
    async def increment_referral_count(user_id: int) -> bool:
        try:
            async with get_db() as db:
                await db.execute(
                    "UPDATE users SET referral_count = COALESCE(referral_count, 0) + 1 WHERE user_id = ?",
                    (user_id,)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to increment referral count for {user_id}: {e}")
            return False
    
    @staticmethod
    async def mark_bonus_given(user_id: int) -> bool:
        try:
            async with get_db() as db:
                await db.execute(
                    "UPDATE users SET referral_bonus_given = 1 WHERE user_id = ?", (user_id,)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to mark bonus given for {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_top_referrers(limit: int = 10) -> List[Dict[str, Any]]:
        """Get top referrers all time."""
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT user_id, username, fullname, referral_count 
                    FROM users 
                    WHERE referral_count > 0 
                    ORDER BY referral_count DESC 
                    LIMIT ?
                """, (limit,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get top referrers: {e}")
            return []
    
    @staticmethod
    async def get_top_referrers_by_period(days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top referrers for the last N days."""
        try:
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT 
                        u.user_id,
                        u.username,
                        u.fullname,
                        COUNT(r.user_id) as referral_count
                    FROM users u
                    LEFT JOIN users r ON r.referred_by = u.user_id 
                        AND r.referral_bonus_given = 1
                        AND r.registration_date >= ?
                    GROUP BY u.user_id, u.username, u.fullname
                    HAVING COUNT(r.user_id) > 0
                    ORDER BY referral_count DESC
                    LIMIT ?
                """, (cutoff_date, limit))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get top referrers by period: {e}")
            return []
    
    @staticmethod
    async def get_active_referral_count(user_id: int) -> int:
        """Count referrals where referral_bonus_given = 1 (completed registration)."""
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM users WHERE referred_by = ? AND referral_bonus_given = 1",
                    (user_id,)
                )
                result = await cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Failed to get active referral count for {user_id}: {e}")
            return 0

    @staticmethod
    async def get_total_referrals() -> int:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT SUM(referral_count) as total FROM users")
                result = await cursor.fetchone()
                return result['total'] if result and result['total'] else 0
        except Exception as e:
            logger.error(f"❌ Failed to get total referrals: {e}")
            return 0


referral_repo = ReferralRepository()
