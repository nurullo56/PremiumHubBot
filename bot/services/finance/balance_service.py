# bot/services/finance/balance_service.py
"""Balance service with atomic operations and zero race conditions."""

import logging
from decimal import Decimal
from typing import Tuple, Dict, Any, Optional

from bot.database.repositories.balance_repo import balance_repo
from bot.database.base import get_db
from bot.utils.common.timezone import now_str
from bot.utils.common.money import to_scaled, from_scaled, format_balance as _fmt
from bot.config.constants import (
    TRANSACTION_REFERRAL_BONUS,
    TRANSACTION_ADMIN_ADD,
    TRANSACTION_ADMIN_SUBTRACT,
    BALANCE_MAX_OLMOS,
)

logger = logging.getLogger(__name__)

MINIMUM_BALANCE = Decimal('0')
MAXIMUM_BALANCE = Decimal(str(BALANCE_MAX_OLMOS))


class BalanceService:
    """
    Balance service with production-ready atomic operations.

    Key features:
    - Integer scaling (1 olmos = 100 cents) for precision
    - RETURNING clause for atomic updates
    - BEGIN IMMEDIATE for exclusive locks
    - Zero race conditions
    - Type-safe Decimal interface
    """
    
    async def get_balance(self, user_id: int) -> Decimal:
        """Get current balance (Decimal)."""
        try:
            return await balance_repo.get_balance(user_id)
        except Exception as e:
            logger.error(f"❌ get_balance error for {user_id}: {e}")
            return Decimal('0')
    
    async def add_balance(
        self,
        user_id: int,
        amount: Decimal,
        description: str = "",
        transaction_type: str = TRANSACTION_ADMIN_ADD
    ) -> Tuple[bool, str, Decimal]:
        """
        Add balance with atomic operation using RETURNING.
        
        Args:
            user_id: User ID
            amount: Amount to add (Decimal)
            description: Transaction description
            transaction_type: Type of transaction
            
        Returns:
            Tuple[bool, str, Decimal]: (success, message, new_balance)
        """
        if amount <= 0:
            return False, "Miqdor musbat bo'lishi kerak", Decimal('0')
        
        if amount > MAXIMUM_BALANCE:
            return False, f"Maksimal qo'shish limiti {MAXIMUM_BALANCE}💎", Decimal('0')
        
        try:
            async with get_db() as db:
                await db.execute("BEGIN IMMEDIATE")
                
                try:
                    # Convert to scaled integer
                    scaled_amount = to_scaled(amount)
                    scaled_max = to_scaled(MAXIMUM_BALANCE)
                    
                    # Atomic update with RETURNING
                    cursor = await db.execute("""
                        UPDATE users 
                        SET balance_scaled = COALESCE(balance_scaled, 0) + ?
                        WHERE user_id = ? 
                          AND (COALESCE(balance_scaled, 0) + ?) <= ?
                        RETURNING balance_scaled
                    """, (scaled_amount, user_id, scaled_amount, scaled_max))
                    
                    result = await cursor.fetchone()
                    
                    if not result:
                        await db.rollback()
                        current = await self.get_balance(user_id)
                        if current + amount > MAXIMUM_BALANCE:
                            return False, f"Maksimal balans limiti {MAXIMUM_BALANCE}💎 dan oshib ketdi", current
                        return False, "Foydalanuvchi topilmadi", Decimal('0')
                    
                    new_balance_scaled = result['balance_scaled']
                    new_balance = from_scaled(new_balance_scaled)

                    # Add history
                    timestamp = now_str()
                    await balance_repo.add_history_scaled(
                        db=db,
                        user_id=user_id,
                        amount_scaled=scaled_amount,
                        description=description,
                        new_balance_scaled=new_balance_scaled,
                        transaction_type=transaction_type,
                        timestamp=timestamp
                    )
                    
                    await db.commit()
                    
                    logger.info(f"✅ Balance added: user={user_id}, +{amount}, new={new_balance}")
                    return True, "Balans qo'shildi", new_balance
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"❌ add_balance transaction error for {user_id}: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"❌ add_balance error for {user_id}: {e}")
            return False, f"Xatolik: {str(e)}", Decimal('0')
    
    async def subtract_balance(
        self,
        user_id: int,
        amount: Decimal,
        description: str = "",
        transaction_type: str = TRANSACTION_ADMIN_SUBTRACT
    ) -> Tuple[bool, str, Decimal]:
        """
        Subtract balance with atomic check using RETURNING.
        
        Args:
            user_id: User ID
            amount: Amount to subtract (Decimal)
            description: Transaction description
            transaction_type: Type of transaction
            
        Returns:
            Tuple[bool, str, Decimal]: (success, message, new_balance)
        """
        if amount <= 0:
            return False, "Miqdor musbat bo'lishi kerak", Decimal('0')
        
        try:
            async with get_db() as db:
                await db.execute("BEGIN IMMEDIATE")
                
                try:
                    # Convert to scaled integer
                    scaled_amount = to_scaled(amount)

                    # Atomic update with balance check and RETURNING
                    cursor = await db.execute("""
                        UPDATE users 
                        SET balance_scaled = balance_scaled - ?
                        WHERE user_id = ? 
                          AND COALESCE(balance_scaled, 0) >= ?
                        RETURNING balance_scaled
                    """, (scaled_amount, user_id, scaled_amount))
                    
                    result = await cursor.fetchone()
                    
                    if not result:
                        await db.rollback()
                        current = await self.get_balance(user_id)
                        return False, "Balansingizda yetarli mablag' yo'q", current
                    
                    new_balance_scaled = result['balance_scaled']
                    new_balance = from_scaled(new_balance_scaled)

                    # Add history (negative amount)
                    timestamp = now_str()
                    await balance_repo.add_history_scaled(
                        db=db,
                        user_id=user_id,
                        amount_scaled=-scaled_amount,
                        description=description,
                        new_balance_scaled=new_balance_scaled,
                        transaction_type=transaction_type,
                        timestamp=timestamp
                    )
                    
                    await db.commit()
                    
                    logger.info(f"✅ Balance subtracted: user={user_id}, -{amount}, new={new_balance}")
                    return True, "Balans ayirildi", new_balance
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"❌ subtract_balance transaction error for {user_id}: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"❌ subtract_balance error for {user_id}: {e}")
            current = await self.get_balance(user_id)
            return False, f"Xatolik: {str(e)}", current
    
    async def transfer_balance(
        self,
        from_user_id: int,
        to_user_id: int,
        amount: Decimal,
        description: str = ""
    ) -> Tuple[bool, str, Decimal]:
        """
        Atomic transfer with zero race conditions.
        
        Uses:
        - BEGIN IMMEDIATE for exclusive lock
        - RETURNING clause for atomicity
        - Same transaction for both operations
        
        Args:
            from_user_id: Sender user ID
            to_user_id: Receiver user ID
            amount: Amount to transfer (Decimal)
            description: Transfer description
            
        Returns:
            Tuple[bool, str, Decimal]: (success, message, new_from_balance)
        """
        if from_user_id == to_user_id:
            return False, "O'zingizga o'tkaza olmaysiz", Decimal('0')
        
        if amount <= 0:
            return False, "Miqdor musbat bo'lishi kerak", Decimal('0')
        
        try:
            async with get_db() as db:
                await db.execute("BEGIN IMMEDIATE")
                
                try:
                    scaled_amount = to_scaled(amount)
                    timestamp = now_str()

                    # 1. Subtract from sender (atomic with balance check)
                    cursor = await db.execute("""
                        UPDATE users 
                        SET balance_scaled = balance_scaled - ?
                        WHERE user_id = ? 
                          AND COALESCE(balance_scaled, 0) >= ?
                        RETURNING balance_scaled
                    """, (scaled_amount, from_user_id, scaled_amount))
                    
                    from_result = await cursor.fetchone()
                    
                    if not from_result:
                        await db.rollback()
                        from_balance = await self.get_balance(from_user_id)
                        return False, f"Balans yetarli emas. Sizda {_fmt(from_balance)}", from_balance

                    new_from_balance_scaled = from_result['balance_scaled']
                    new_from_balance = from_scaled(new_from_balance_scaled)
                    
                    # 2. Add to receiver (atomic)
                    cursor = await db.execute("""
                        UPDATE users 
                        SET balance_scaled = COALESCE(balance_scaled, 0) + ?
                        WHERE user_id = ?
                        RETURNING balance_scaled
                    """, (scaled_amount, to_user_id))
                    
                    to_result = await cursor.fetchone()
                    
                    if not to_result:
                        await db.rollback()
                        return False, "Qabul qiluvchi topilmadi", Decimal('0')
                    
                    new_to_balance_scaled = to_result['balance_scaled']
                    
                    # 3. Add history for both (in same transaction)
                    await balance_repo.add_history_scaled(
                        db=db,
                        user_id=from_user_id,
                        amount_scaled=-scaled_amount,
                        description=f"Transfer to {to_user_id}: {description}",
                        new_balance_scaled=new_from_balance_scaled,
                        transaction_type="transfer_out",
                        timestamp=timestamp
                    )
                    
                    await balance_repo.add_history_scaled(
                        db=db,
                        user_id=to_user_id,
                        amount_scaled=scaled_amount,
                        description=f"Transfer from {from_user_id}: {description}",
                        new_balance_scaled=new_to_balance_scaled,
                        transaction_type="transfer_in",
                        timestamp=timestamp
                    )
                    
                    await db.commit()

                    logger.info(f"✅ Transfer: {from_user_id} → {to_user_id} ({amount}💎)")
                    return True, f"{_fmt(amount)} muvaffaqiyatli o'tkazildi", new_from_balance
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"❌ Transfer transaction error: {e}")
                    raise
                    
        except Exception as e:
            logger.error(f"❌ transfer_balance error: {e}")
            return False, f"Xatolik: {str(e)}", Decimal('0')
    
    async def set_balance(self, user_id: int, amount: Decimal) -> bool:
        """Set balance (admin operation)."""
        if amount < MINIMUM_BALANCE or amount > MAXIMUM_BALANCE:
            logger.warning(f"⚠️ Invalid balance amount: {amount}")
            return False
        
        try:
            scaled_amount = to_scaled(amount)
            return await balance_repo.set_balance_scaled(user_id, scaled_amount)
        except Exception as e:
            logger.error(f"❌ set_balance error for {user_id}: {e}")
            return False
    
    async def get_history(self, user_id: int, limit: int = 50):
        """Get balance history."""
        try:
            return await balance_repo.get_history(user_id, limit)
        except Exception as e:
            logger.error(f"❌ get_history error for {user_id}: {e}")
            return []
    
    async def get_top_users(self, limit: int = 10):
        """Get top users by balance."""
        try:
            return await balance_repo.get_top_users(limit)
        except Exception as e:
            logger.error(f"❌ get_top_users error: {e}")
            return []
    
    async def format_balance(self, balance: Decimal) -> str:
        """Format balance for display. Kept async for backward compatibility with existing call sites."""
        return _fmt(balance)
    
    async def get_balance_stats(self) -> Dict[str, Any]:
        """Get balance statistics."""
        try:
            async with get_db() as db:
                # Total balance
                cursor = await db.execute(
                    "SELECT SUM(balance_scaled) as total FROM users WHERE is_blocked = 0"
                )
                total_result = await cursor.fetchone()
                total_scaled = total_result['total'] if total_result and total_result['total'] else 0
                total_balance = from_scaled(total_scaled)
                
                # Average balance
                cursor = await db.execute(
                    "SELECT AVG(balance_scaled) as avg FROM users WHERE balance_scaled > 0 AND is_blocked = 0"
                )
                avg_result = await cursor.fetchone()
                avg_scaled = avg_result['avg'] if avg_result and avg_result['avg'] else 0
                avg_balance = from_scaled(int(avg_scaled))
                
                # Users with balance count
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM users WHERE balance_scaled > 0 AND is_blocked = 0"
                )
                count_result = await cursor.fetchone()
                users_with_balance = count_result['count'] if count_result else 0
                
                # Max balance
                cursor = await db.execute(
                    "SELECT MAX(balance_scaled) as max FROM users WHERE is_blocked = 0"
                )
                max_result = await cursor.fetchone()
                max_scaled = max_result['max'] if max_result and max_result['max'] else 0
                max_balance = from_scaled(max_scaled)
                
                # Min balance (> 0)
                cursor = await db.execute(
                    "SELECT MIN(balance_scaled) as min FROM users WHERE balance_scaled > 0 AND is_blocked = 0"
                )
                min_result = await cursor.fetchone()
                min_scaled = min_result['min'] if min_result and min_result['min'] else 0
                min_balance = from_scaled(min_scaled)
                
                # Median balance
                cursor = await db.execute("""
                    SELECT balance_scaled 
                    FROM users 
                    WHERE balance_scaled > 0 AND is_blocked = 0 
                    ORDER BY balance_scaled 
                    LIMIT 1 OFFSET (SELECT COUNT(*) FROM users WHERE balance_scaled > 0 AND is_blocked = 0) / 2
                """)
                median_result = await cursor.fetchone()
                median_scaled = median_result['balance_scaled'] if median_result else 0
                median_balance = from_scaled(median_scaled)
                
                return {
                    'total_balance': total_balance,
                    'average_balance': avg_balance,
                    'median_balance': median_balance,
                    'users_with_balance': users_with_balance,
                    'max_balance': max_balance,
                    'min_balance': min_balance
                }
                
        except Exception as e:
            logger.error(f"❌ get_balance_stats error: {e}")
            return {
                'total_balance': Decimal('0'),
                'average_balance': Decimal('0'),
                'median_balance': Decimal('0'),
                'users_with_balance': 0,
                'max_balance': Decimal('0'),
                'min_balance': Decimal('0')
            }
    
    async def get_balance_rank(self, user_id: int) -> Tuple[int, int]:
        """Get user's balance rank."""
        try:
            balance = await self.get_balance(user_id)
            scaled_balance = to_scaled(balance)
            
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM users WHERE balance_scaled > ? AND is_blocked = 0",
                    (scaled_balance,)
                )
                higher_count = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE is_blocked = 0")
                total = (await cursor.fetchone())['count']
                
                return higher_count + 1, total
                
        except Exception as e:
            logger.error(f"❌ get_balance_rank error for {user_id}: {e}")
            return 0, 0


balance_service = BalanceService()