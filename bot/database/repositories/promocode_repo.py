"""Promocode repository - database access only."""

import logging
from typing import List, Dict, Any, Optional

from bot.database.base import get_db

logger = logging.getLogger(__name__)


class PromocodeRepository:
    
    @staticmethod
    async def create(
        code: str,
        user_id: int,
        username: Optional[str],
        fullname: str,
        product_name: str,
        product_price: float,
        created_date: str,
        expiry_date: Optional[str] = None,
        usage_limit: int = 1
    ) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    INSERT INTO promocodes (
                        code, user_id, username, fullname, product_name, product_price,
                        created_date, expiry_date, usage_limit
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (code, user_id, username, fullname, product_name, product_price, 
                      created_date, expiry_date, usage_limit))
                await db.commit()
                logger.info(f"✅ Promocode created: {code}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create promocode {code}: {e}")
            return False
    
    @staticmethod
    async def get_by_code(code: str) -> Optional[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT * FROM promocodes WHERE code = ?", (code,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get promocode {code}: {e}")
            return None
    
    @staticmethod
    async def get_by_user(user_id: int) -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT * FROM promocodes WHERE user_id = ? ORDER BY created_date DESC",
                    (user_id,)
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get promocodes for user {user_id}: {e}")
            return []
    
    @staticmethod
    async def mark_used(code: str, used_by: int, used_date: str) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    UPDATE promocodes 
                    SET is_used = 1, used_by = ?, used_date = ?, usage_count = usage_count + 1
                    WHERE code = ?
                """, (used_by, used_date, code))
                await db.commit()
                logger.info(f"✅ Promocode marked used: {code}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to mark promocode used {code}: {e}")
            return False
    
    @staticmethod
    async def get_unused_count(user_id: int) -> int:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM promocodes WHERE user_id = ? AND is_used = 0",
                    (user_id,)
                )
                result = await cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Failed to get unused promocode count for {user_id}: {e}")
            return 0
    
    @staticmethod
    async def get_all(limit: int = 100) -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT * FROM promocodes ORDER BY created_date DESC LIMIT ?", (limit,)
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get all promocodes: {e}")
            return []


promocode_repo = PromocodeRepository()
