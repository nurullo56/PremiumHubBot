# bot/database/repositories/balance_repo.py
"""Balance repository with integer scaling for precision."""

import logging
from decimal import Decimal
from typing import Tuple, List, Dict, Any, Optional

import aiosqlite

from bot.database.base import get_db
from bot.utils.common.money import to_scaled, from_scaled

logger = logging.getLogger(__name__)


class BalanceRepository:
    """
    Balance repository with scaled integer storage.
    
    CRITICAL:
    - balance_scaled: INTEGER (1 olmos = 100 cents)
    - All DB operations use scaled integers
    - Conversion to Decimal happens in service layer
    - RETURNING clause for atomicity
    - No race conditions
    """
    
    # ==================== CORE BALANCE METHODS ====================
    
    async def get_balance(self, user_id: int) -> Decimal:
        """
        Get user balance (returns Decimal).
        
        Uses balance_scaled column for precision.
        
        Args:
            user_id: User ID
            
        Returns:
            Balance as Decimal (e.g., Decimal('10.50'))
        """
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT balance_scaled FROM users WHERE user_id = ?",
                    (user_id,)
                )
                result = await cursor.fetchone()
                
                if result and result['balance_scaled'] is not None:
                    return from_scaled(result['balance_scaled'])
                
                return Decimal('0')
                
        except Exception as e:
            logger.error(f"❌ get_balance error for {user_id}: {e}")
            return Decimal('0')
    
    async def get_balance_scaled(self, user_id: int) -> int:
        """
        Get user balance as scaled integer (for internal use).
        
        Args:
            user_id: User ID
            
        Returns:
            Scaled balance (e.g., 1050 for 10.50 olmos)
        """
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT balance_scaled FROM users WHERE user_id = ?",
                    (user_id,)
                )
                result = await cursor.fetchone()
                
                if result and result['balance_scaled'] is not None:
                    return result['balance_scaled']
                
                return 0
                
        except Exception as e:
            logger.error(f"❌ get_balance_scaled error for {user_id}: {e}")
            return 0
    
    async def set_balance_scaled(self, user_id: int, scaled_amount: int) -> bool:
        """
        Set balance (direct scaled integer).
        
        Args:
            user_id: User ID
            scaled_amount: Scaled integer amount
            
        Returns:
            True if successful
        """
        try:
            async with get_db() as db:
                await db.execute(
                    "UPDATE users SET balance_scaled = ? WHERE user_id = ?",
                    (scaled_amount, user_id)
                )
                await db.commit()
                
                balance = from_scaled(scaled_amount)
                logger.info(f"✅ Balance set: user={user_id}, balance={balance}")
                return True
                
        except Exception as e:
            logger.error(f"❌ set_balance_scaled error for {user_id}: {e}")
            return False
    
    # ==================== LEGACY METHODS (Backward Compatibility) ====================
    
    async def add_balance(self, user_id: int, amount: Decimal) -> Tuple[bool, Decimal]:
        """
        Legacy method for backward compatibility.
        
        NOTE: Prefer using atomic operations in balance_service.py
        
        Args:
            user_id: User ID
            amount: Amount to add (Decimal)
            
        Returns:
            Tuple[bool, Decimal]: (success, new_balance)
        """
        try:
            async with get_db() as db:
                scaled_amount = to_scaled(amount)
                
                cursor = await db.execute(
                    "UPDATE users SET balance_scaled = COALESCE(balance_scaled, 0) + ? WHERE user_id = ?",
                    (scaled_amount, user_id)
                )
                
                if cursor.rowcount == 0:
                    return False, Decimal('0')
                
                await db.commit()
                new_balance = await self.get_balance(user_id)
                logger.info(f"💰 Balance added: user={user_id}, +{amount}, new={new_balance}")
                return True, new_balance
                
        except Exception as e:
            logger.error(f"❌ add_balance error for {user_id}: {e}")
            return False, Decimal('0')
    
    async def subtract_balance(self, user_id: int, amount: Decimal) -> Tuple[bool, Decimal]:
        """
        Legacy method for backward compatibility.
        
        NOTE: Prefer using atomic operations in balance_service.py
        
        Args:
            user_id: User ID
            amount: Amount to subtract (Decimal)
            
        Returns:
            Tuple[bool, Decimal]: (success, new_balance)
        """
        try:
            async with get_db() as db:
                scaled_amount = to_scaled(amount)
                
                cursor = await db.execute(
                    "UPDATE users SET balance_scaled = balance_scaled - ? WHERE user_id = ? AND COALESCE(balance_scaled, 0) >= ?",
                    (scaled_amount, user_id, scaled_amount)
                )
                
                if cursor.rowcount == 0:
                    return False, Decimal('0')
                
                await db.commit()
                new_balance = await self.get_balance(user_id)
                logger.info(f"💸 Balance subtracted: user={user_id}, -{amount}, new={new_balance}")
                return True, new_balance
                
        except Exception as e:
            logger.error(f"❌ subtract_balance error for {user_id}: {e}")
            return False, Decimal('0')
    
    # ==================== HISTORY METHODS ====================
    
    async def add_history_scaled(
        self,
        db: aiosqlite.Connection,
        user_id: int,
        amount_scaled: int,
        description: str,
        new_balance_scaled: int,
        transaction_type: str,
        timestamp: str
    ) -> bool:
        """
        Add balance history entry (within transaction).
        
        CRITICAL: This method expects an active db connection.
        It does NOT commit - the caller must commit.
        
        Args:
            db: Database connection (in transaction)
            user_id: User ID
            amount_scaled: Scaled amount (can be negative)
            description: Transaction description
            new_balance_scaled: New balance (scaled)
            transaction_type: Type of transaction
            timestamp: Transaction timestamp
            
        Returns:
            True if successful
        """
        try:
            await db.execute("""
                INSERT INTO balance_history (
                    user_id, amount_scaled, description, 
                    new_balance_scaled, transaction_type, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                amount_scaled,
                description,
                new_balance_scaled,
                transaction_type,
                timestamp
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ add_history_scaled error for {user_id}: {e}")
            return False
    
    async def add_history(
        self,
        user_id: int,
        amount: Decimal,
        description: str,
        new_balance: Decimal,
        transaction_type: str,
        timestamp: str
    ) -> bool:
        """
        Legacy method for backward compatibility.
        
        Converts Decimal to scaled integers.
        
        Args:
            user_id: User ID
            amount: Amount (Decimal)
            description: Transaction description
            new_balance: New balance (Decimal)
            transaction_type: Type of transaction
            timestamp: Transaction timestamp
            
        Returns:
            True if successful
        """
        try:
            async with get_db() as db:
                amount_scaled = to_scaled(amount)
                new_balance_scaled = to_scaled(new_balance)
                
                await db.execute("""
                    INSERT INTO balance_history (
                        user_id, amount_scaled, description, 
                        new_balance_scaled, transaction_type, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    amount_scaled,
                    description,
                    new_balance_scaled,
                    transaction_type,
                    timestamp
                ))
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ add_history error for {user_id}: {e}")
            return False
    
    async def get_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get balance history (converted to Decimal for display).
        
        Args:
            user_id: User ID
            limit: Maximum number of records
            
        Returns:
            List of history records with Decimal amounts
        """
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT * FROM balance_history 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                rows = await cursor.fetchall()
                
                # Convert scaled amounts to Decimal for display
                history = []
                for row in rows:
                    record = dict(row)
                    
                    # Convert scaled integers to Decimal
                    if 'amount_scaled' in record and record['amount_scaled'] is not None:
                        record['amount'] = from_scaled(record['amount_scaled'])
                    
                    if 'new_balance_scaled' in record and record['new_balance_scaled'] is not None:
                        record['new_balance'] = from_scaled(record['new_balance_scaled'])
                    
                    history.append(record)
                
                return history
                
        except Exception as e:
            logger.error(f"❌ get_history error for {user_id}: {e}")
            return []
    
    # ==================== STATISTICS METHODS ====================
    
    async def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top users by balance.
        
        Args:
            limit: Maximum number of users
            
        Returns:
            List of user records with Decimal balances
        """
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT user_id, username, fullname, balance_scaled 
                    FROM users 
                    WHERE balance_scaled > 0 
                    ORDER BY balance_scaled DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = await cursor.fetchall()
                
                # Convert to Decimal for display
                users = []
                for row in rows:
                    user = dict(row)
                    if 'balance_scaled' in user and user['balance_scaled'] is not None:
                        user['balance'] = from_scaled(user['balance_scaled'])
                    users.append(user)
                
                return users
                
        except Exception as e:
            logger.error(f"❌ get_top_users error: {e}")
            return []
    
    async def get_total_balance(self) -> Decimal:
        """
        Get total balance across all users.
        
        Returns:
            Total balance as Decimal
        """
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT SUM(balance_scaled) as total FROM users"
                )
                result = await cursor.fetchone()
                
                if result and result['total'] is not None:
                    return from_scaled(result['total'])
                
                return Decimal('0')
                
        except Exception as e:
            logger.error(f"❌ get_total_balance error: {e}")
            return Decimal('0')
    
    async def get_users_with_balance_count(self) -> int:
        """
        Get count of users with positive balance.
        
        Returns:
            Count of users
        """
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM users WHERE balance_scaled > 0"
                )
                result = await cursor.fetchone()
                return result['count'] if result else 0
                
        except Exception as e:
            logger.error(f"❌ get_users_with_balance_count error: {e}")
            return 0
    
    # ==================== CLEANUP METHODS ====================
    
    async def cleanup_old_history(self, days: int = 90) -> int:
        """
        Clean up old balance history (performance optimization).
        
        Args:
            days: Keep history for last N days
            
        Returns:
            Number of deleted records
        """
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            async with get_db() as db:
                cursor = await db.execute("""
                    DELETE FROM balance_history
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                deleted_count = cursor.rowcount
                await db.commit()
                
                logger.info(f"✅ Cleaned up {deleted_count} old balance history records (>{days} days)")
                return deleted_count
                
        except Exception as e:
            logger.error(f"❌ cleanup_old_history error: {e}")
            return 0


balance_repo = BalanceRepository()