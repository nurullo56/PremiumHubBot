"""Balance service - business logic."""

import logging
from decimal import Decimal
from typing import Tuple, Dict, Any, List, Optional

from bot.database.repositories.balance_repo import balance_repo
from bot.utils.common.timezone import now_str
from bot.config.constants import TRANSACTION_REFERRAL_BONUS, TRANSACTION_ADMIN_ADD

logger = logging.getLogger(__name__)

MINIMUM_BALANCE = Decimal('0')
MAXIMUM_BALANCE = Decimal('1000000')


class BalanceService:
    
    async def get_balance(self, user_id: int) -> Decimal:
        return await balance_repo.get_balance(user_id)
    
    async def add_balance(
        self,
        user_id: int,
        amount: Decimal,
        description: str = "",
        transaction_type: str = TRANSACTION_ADMIN_ADD
    ) -> Tuple[bool, str, Decimal]:
        if amount <= 0:
            return False, "Miqdor musbat bo'lishi kerak", Decimal('0')
        
        current = await balance_repo.get_balance(user_id)
        if current + amount > MAXIMUM_BALANCE:
            return False, f"Maksimal balans limiti {MAXIMUM_BALANCE}💎 dan oshib ketdi", current
        
        success, new_balance = await balance_repo.add_balance(user_id, amount)
        
        if success:
            timestamp = now_str()
            await balance_repo.add_history(
                user_id=user_id,
                amount=amount,
                description=description,
                new_balance=new_balance,
                transaction_type=transaction_type,
                timestamp=timestamp
            )
            return True, "Balans qo'shildi", new_balance
        else:
            return False, "Xatolik yuz berdi", Decimal('0')
    
    async def subtract_balance(
        self,
        user_id: int,
        amount: Decimal,
        description: str = ""
    ) -> Tuple[bool, str, Decimal]:
        if amount <= 0:
            return False, "Miqdor musbat bo'lishi kerak", Decimal('0')
        
        current = await balance_repo.get_balance(user_id)
        if current < amount:
            return False, "Balansingizda yetarli mablag' yo'q", current
        
        success, new_balance = await balance_repo.subtract_balance(user_id, amount)
        
        if success:
            timestamp = now_str()
            await balance_repo.add_history(
                user_id=user_id,
                amount=-amount,
                description=description,
                new_balance=new_balance,
                transaction_type="subtract",
                timestamp=timestamp
            )
            return True, "Balans ayirildi", new_balance
        else:
            return False, "Xatolik yuz berdi", current
    
    async def set_balance(self, user_id: int, amount: Decimal) -> bool:
        if amount < MINIMUM_BALANCE or amount > MAXIMUM_BALANCE:
            logger.warning(f"⚠️ Invalid balance amount: {amount}")
            return False
        
        return await balance_repo.set_balance(user_id, amount)
    
    async def get_history(self, user_id: int, limit: int = 50):
        return await balance_repo.get_history(user_id, limit)
    
    async def get_top_users(self, limit: int = 10):
        return await balance_repo.get_top_users(limit)
    
    async def format_balance(self, balance: Decimal) -> str:
        if balance == int(balance):
            return f"{int(balance):,}💎"
        else:
            return f"{balance:,.2f}💎"

# ===================== TRANSFER BALANCE =====================

async def transfer_balance(
    self,
    from_user_id: int,
    to_user_id: int,
    amount: Decimal,
    description: str = ""
) -> Tuple[bool, str, Decimal]:
    """
    Bir foydalanuvchidan ikkinchisiga balans o'tkazish
    
    Args:
        from_user_id: Kimdan
        to_user_id: Kimga
        amount: Miqdor
        description: Tavsif
    
    Returns:
        Tuple[bool, str, Decimal]: (success, message, new_from_balance)
    """
    try:
        if from_user_id == to_user_id:
            return False, "O'zingizga o'tkaza olmaysiz", Decimal('0')
        
        if amount <= 0:
            return False, "Miqdor musbat bo'lishi kerak", Decimal('0')
        
        from_balance = await self.get_balance(from_user_id)
        if from_balance < amount:
            return False, f"Balans yetarli emas. Sizda {await self.format_balance(from_balance)}", from_balance
        
        # Atomic transfer using database transaction
        from bot.database.base import get_db
        
        async with get_db() as db:
            try:
                await db.execute("BEGIN IMMEDIATE")
                
                # 1. Kimdan pul yechish
                cursor = await db.execute(
                    "UPDATE users SET balance = balance - ? WHERE user_id = ? AND balance >= ?",
                    (float(amount), from_user_id, float(amount))
                )
                
                if cursor.rowcount == 0:
                    await db.rollback()
                    return False, "Balans yetarli emas", from_balance
                
                # 2. Kimga pul qo'shish
                cursor = await db.execute(
                    "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                    (float(amount), to_user_id)
                )
                
                if cursor.rowcount == 0:
                    await db.rollback()
                    return False, "Qabul qiluvchi topilmadi", from_balance
                
                await db.commit()
                
                # 3. History saqlash
                timestamp = now_str()
                new_from_balance = await self.get_balance(from_user_id)
                new_to_balance = await self.get_balance(to_user_id)
                
                await balance_repo.add_history(
                    from_user_id, -amount, f"Transfer to {to_user_id}: {description}",
                    new_from_balance, "transfer_out", timestamp
                )
                await balance_repo.add_history(
                    to_user_id, amount, f"Transfer from {from_user_id}: {description}",
                    new_to_balance, "transfer_in", timestamp
                )
                
                logger.info(f"✅ Transfer: {from_user_id} → {to_user_id} ({amount}💎)")
                return True, f"{await self.format_balance(amount)} muvaffaqiyatli o'tkazildi", new_from_balance
                
            except Exception as e:
                await db.rollback()
                logger.error(f"❌ Transfer error: {e}")
                return False, f"Xatolik: {str(e)}", from_balance
                
    except Exception as e:
        logger.error(f"❌ Transfer balance error: {e}")
        return False, f"Xatolik: {str(e)}", Decimal('0')


# ===================== BALANCE STATISTICS =====================

async def get_balance_stats(self) -> Dict[str, Any]:
    """
    Balans statistikasi
    
    Returns:
        dict: {
            'total_balance': Decimal,
            'average_balance': Decimal,
            'median_balance': Decimal,
            'users_with_balance': int,
            'max_balance': Decimal,
            'min_balance': Decimal
        }
    """
    try:
        async with get_db() as db:
            # Umumiy balans
            cursor = await db.execute("SELECT SUM(balance) as total FROM users WHERE is_blocked = 0")
            total_result = await cursor.fetchone()
            total_balance = Decimal(str(total_result['total'])) if total_result and total_result['total'] else Decimal('0')
            
            # O'rtacha balans
            cursor = await db.execute("SELECT AVG(balance) as avg FROM users WHERE balance > 0 AND is_blocked = 0")
            avg_result = await cursor.fetchone()
            avg_balance = Decimal(str(avg_result['avg'])) if avg_result and avg_result['avg'] else Decimal('0')
            
            # Balansi bor userlar soni
            cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE balance > 0 AND is_blocked = 0")
            count_result = await cursor.fetchone()
            users_with_balance = count_result['count'] if count_result else 0
            
            # Maksimal balans
            cursor = await db.execute("SELECT MAX(balance) as max FROM users WHERE is_blocked = 0")
            max_result = await cursor.fetchone()
            max_balance = Decimal(str(max_result['max'])) if max_result and max_result['max'] else Decimal('0')
            
            # Minimal balans (0 dan katta)
            cursor = await db.execute("SELECT MIN(balance) as min FROM users WHERE balance > 0 AND is_blocked = 0")
            min_result = await cursor.fetchone()
            min_balance = Decimal(str(min_result['min'])) if min_result and min_result['min'] else Decimal('0')
            
            # Median balans
            cursor = await db.execute("""
                SELECT balance 
                FROM users 
                WHERE balance > 0 AND is_blocked = 0 
                ORDER BY balance 
                LIMIT 1 OFFSET (SELECT COUNT(*) FROM users WHERE balance > 0 AND is_blocked = 0) / 2
            """)
            median_result = await cursor.fetchone()
            median_balance = Decimal(str(median_result['balance'])) if median_result else Decimal('0')
            
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
    """
    Foydalanuvchining balans reytingini olish
    
    Args:
        user_id: User ID
    
    Returns:
        Tuple[int, int]: (rank, total_users)
    """
    try:
        balance = await self.get_balance(user_id)
        
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT COUNT(*) as count FROM users WHERE balance > ? AND is_blocked = 0",
                (float(balance),)
            )
            higher_count = (await cursor.fetchone())['count']
            
            cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE is_blocked = 0")
            total = (await cursor.fetchone())['count']
            
            return higher_count + 1, total
            
    except Exception as e:
        logger.error(f"❌ get_balance_rank error {user_id}: {e}")
        return 0, 0


balance_service = BalanceService()
