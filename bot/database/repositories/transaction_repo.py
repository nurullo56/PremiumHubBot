"""Transaction repository - database access only."""

import logging
from typing import List, Dict, Any

from bot.database.base import get_db

logger = logging.getLogger(__name__)


class TransactionRepository:
    
    @staticmethod
    async def create(
        user_id: int,
        transaction_type: str,
        amount: float,
        description: str,
        created_at: str
    ) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    INSERT INTO transactions (user_id, transaction_type, amount, description, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, transaction_type, amount, description, created_at))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create transaction for {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_by_user(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT * FROM transactions 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get transactions for {user_id}: {e}")
            return []
    
    @staticmethod
    async def get_by_type(transaction_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT * FROM transactions 
                    WHERE transaction_type = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (transaction_type, limit))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get transactions by type {transaction_type}: {e}")
            return []
    
    @staticmethod
    async def get_total_count() -> int:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT COUNT(*) as count FROM transactions")
                result = await cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Failed to get total transaction count: {e}")
            return 0


transaction_repo = TransactionRepository()
