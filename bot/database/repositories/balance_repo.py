"""Balance repository - database access only."""

import logging
from decimal import Decimal
from typing import Tuple, List, Dict, Any

from bot.database.base import get_db

logger = logging.getLogger(__name__)


class BalanceRepository:
    
    @staticmethod
    async def get_balance(user_id: int) -> Decimal:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
                result = await cursor.fetchone()
                return Decimal(str(result['balance'])) if result and result['balance'] is not None else Decimal('0')
        except Exception as e:
            logger.error(f"❌ Failed to get balance for {user_id}: {e}")
            return Decimal('0')
    
    @staticmethod
    async def add_balance(user_id: int, amount: Decimal) -> Tuple[bool, Decimal]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "UPDATE users SET balance = COALESCE(balance, 0) + ? WHERE user_id = ?",
                    (float(amount), user_id)
                )
                
                if cursor.rowcount == 0:
                    return False, Decimal('0')
                
                await db.commit()
                new_balance = await BalanceRepository.get_balance(user_id)
                logger.info(f"💰 Balance added: user={user_id}, +{amount}, new={new_balance}")
                return True, new_balance
        except Exception as e:
            logger.error(f"❌ Failed to add balance for {user_id}: {e}")
            return False, Decimal('0')
    
    @staticmethod
    async def subtract_balance(user_id: int, amount: Decimal) -> Tuple[bool, Decimal]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "UPDATE users SET balance = COALESCE(balance, 0) - ? WHERE user_id = ? AND COALESCE(balance, 0) >= ?",
                    (float(amount), user_id, float(amount))
                )
                
                if cursor.rowcount == 0:
                    return False, Decimal('0')
                
                await db.commit()
                new_balance = await BalanceRepository.get_balance(user_id)
                logger.info(f"💸 Balance subtracted: user={user_id}, -{amount}, new={new_balance}")
                return True, new_balance
        except Exception as e:
            logger.error(f"❌ Failed to subtract balance for {user_id}: {e}")
            return False, Decimal('0')
    
    @staticmethod
    async def set_balance(user_id: int, amount: Decimal) -> bool:
        try:
            async with get_db() as db:
                await db.execute("UPDATE users SET balance = ? WHERE user_id = ?", (float(amount), user_id))
                await db.commit()
                logger.info(f"💰 Balance set: user={user_id}, balance={amount}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to set balance for {user_id}: {e}")
            return False
    
    @staticmethod
    async def add_history(
        user_id: int,
        amount: Decimal,
        description: str,
        new_balance: Decimal,
        transaction_type: str,
        timestamp: str
    ) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    INSERT INTO balance_history (
                        user_id, amount, description, new_balance, transaction_type, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, float(amount), description, float(new_balance), transaction_type, timestamp))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to add balance history for {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT * FROM balance_history 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (user_id, limit))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get balance history for {user_id}: {e}")
            return []
    
    @staticmethod
    async def get_top_users(limit: int = 10) -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT user_id, username, fullname, balance 
                    FROM users 
                    WHERE balance > 0 
                    ORDER BY balance DESC 
                    LIMIT ?
                """, (limit,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get top balance users: {e}")
            return []
    
    @staticmethod
    async def get_total_balance() -> Decimal:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT SUM(balance) as total FROM users")
                result = await cursor.fetchone()
                return Decimal(str(result['total'])) if result and result['total'] else Decimal('0')
        except Exception as e:
            logger.error(f"❌ Failed to get total balance: {e}")
            return Decimal('0')
    
    @staticmethod
    async def get_users_with_balance_count() -> int:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE balance > 0")
                result = await cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Failed to get users with balance count: {e}")
            return 0


balance_repo = BalanceRepository()
