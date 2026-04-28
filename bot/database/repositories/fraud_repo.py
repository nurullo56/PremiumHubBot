"""Fraud repository - database access only."""

import logging
from typing import List, Dict, Any, Optional

from bot.database.base import get_db

logger = logging.getLogger(__name__)


class FraudRepository:
    
    @staticmethod
    async def log_fraud(
        user_id: int,
        action_type: str,
        reason: str,
        created_at: str,
        referral_user_id: Optional[int] = None,
        blocked_until: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    INSERT INTO fraud_logs (
                        user_id, referral_user_id, action_type, reason, 
                        blocked_until, created_at, ip_address
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, referral_user_id, action_type, reason, blocked_until, created_at, ip_address))
                await db.commit()
                logger.warning(f"⚠️ Fraud logged: user={user_id}, type={action_type}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to log fraud for {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_user_logs(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT * FROM fraud_logs 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get fraud logs for {user_id}: {e}")
            return []
    
    @staticmethod
    async def update_rate_limit(user_id: int, action_type: str, timestamp: str) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    INSERT INTO rate_limits (user_id, action_type, request_count, first_request, last_request)
                    VALUES (?, ?, 1, ?, ?)
                    ON CONFLICT(user_id, action_type) 
                    DO UPDATE SET 
                        request_count = request_count + 1,
                        last_request = ?
                """, (user_id, action_type, timestamp, timestamp, timestamp))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update rate limit for {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_rate_limit(user_id: int, action_type: str) -> Optional[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT * FROM rate_limits WHERE user_id = ? AND action_type = ?",
                    (user_id, action_type)
                )
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get rate limit for {user_id}: {e}")
            return None
    
    @staticmethod
    async def track_ip(user_id: int, ip_address: str, timestamp: str) -> bool:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT id FROM ip_tracking WHERE ip_address = ? AND user_id = ?",
                    (ip_address, user_id)
                )
                existing = await cursor.fetchone()
                
                if existing:
                    await db.execute("""
                        UPDATE ip_tracking 
                        SET request_count = request_count + 1, last_seen = ?
                        WHERE ip_address = ? AND user_id = ?
                    """, (timestamp, ip_address, user_id))
                else:
                    await db.execute("""
                        INSERT INTO ip_tracking (ip_address, user_id, first_seen, last_seen, request_count)
                        VALUES (?, ?, ?, ?, 1)
                    """, (ip_address, user_id, timestamp, timestamp))
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to track IP for {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_suspicious_ips() -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT * FROM ip_tracking WHERE is_suspicious = 1"
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get suspicious IPs: {e}")
            return []


fraud_repo = FraudRepository()
