"""Premium service - business logic."""

import logging
from decimal import Decimal
from typing import Tuple, Optional, List, Dict, Any
from datetime import datetime, timedelta

from bot.database.repositories.premium_repo import premium_repo
from bot.config.constants import (
    PREMIUM_STATUS_PENDING,
    PREMIUM_STATUS_ACTIVE,
    PREMIUM_STATUS_REJECTED,
    PREMIUM_STATUS_CANCELLED
)

logger = logging.getLogger(__name__)


class PremiumService:
    
    async def get_status(self, user_id: int) -> Optional[str]:
        return await premium_repo.get_status(user_id)
    
    async def is_premium(self, user_id: int) -> bool:
        status = await premium_repo.get_status(user_id)
        return status in [PREMIUM_STATUS_ACTIVE, 'approved']
    
    async def request_premium(self, user_id: int) -> bool:
        return await premium_repo.set_status(user_id, PREMIUM_STATUS_PENDING)
    
    async def approve_premium(self, user_id: int, expiry: Optional[str] = None) -> bool:
        return await premium_repo.set_status(user_id, PREMIUM_STATUS_ACTIVE, expiry)
    
    async def reject_premium(self, user_id: int) -> bool:
        return await premium_repo.set_status(user_id, PREMIUM_STATUS_REJECTED)
    
    async def cancel_premium(self, user_id: int) -> bool:
        return await premium_repo.set_status(user_id, PREMIUM_STATUS_CANCELLED)
    
    async def mark_admin_notified(self, user_id: int) -> bool:
        return await premium_repo.mark_admin_notified(user_id)
    
    async def get_pending_requests(self) -> List[Dict[str, Any]]:
        return await premium_repo.get_pending()
    
    async def get_active_users(self) -> List[Dict[str, Any]]:
        return await premium_repo.get_active()
    
    async def get_pending_count(self) -> int:
        return await premium_repo.get_count_by_status(PREMIUM_STATUS_PENDING)
    
    async def get_active_count(self) -> int:
        active = await premium_repo.get_count_by_status(PREMIUM_STATUS_ACTIVE)
        approved = await premium_repo.get_count_by_status('approved')
        return active + approved

    # ===================== PREMIUM EXTEND =====================

PREMIUM_DURATIONS = {
    'day': 1,
    'week': 7,
    'month': 30,
    'year': 365,
    'lifetime': 0
}

PREMIUM_PRICES = {
    'day': Decimal('10'),
    'week': Decimal('50'),
    'month': Decimal('150'),
    'year': Decimal('1500'),
    'lifetime': Decimal('5000')
}

REMINDER_DAYS = [7, 3, 1]


async def extend_premium(
    self,
    user_id: int,
    duration: str,
    payment_amount: Optional[Decimal] = None
) -> Tuple[bool, str, Optional[datetime]]:
    """
    Premium muddatini uzaytirish
    
    Args:
        user_id: User ID
        duration: 'day', 'week', 'month', 'year', 'lifetime'
        payment_amount: To'lov miqdori (tekshirish uchun)
    
    Returns:
        Tuple[bool, str, Optional[datetime]]: (success, message, new_expiry)
    """
    try:
        expected_price = PREMIUM_PRICES.get(duration)
        if payment_amount is not None and expected_price:
            if payment_amount < expected_price:
                return False, f"To'lov miqdori yetarli emas. Kerak: {expected_price}💎", None
        
        from bot.database.base import get_db
        
        # Hozirgi expiry ni olish
        current_expiry_str = await self._get_expiry_str(user_id)
        now = datetime.now()
        
        # Yangi expiry hisoblash
        if duration == 'lifetime':
            new_expiry = None
        else:
            days = PREMIUM_DURATIONS.get(duration, 30)
            
            if current_expiry_str:
                try:
                    current_expiry = datetime.fromisoformat(current_expiry_str)
                    if current_expiry > now:
                        new_expiry = current_expiry + timedelta(days=days)
                    else:
                        new_expiry = now + timedelta(days=days)
                except (ValueError, TypeError):
                    new_expiry = now + timedelta(days=days)
            else:
                new_expiry = now + timedelta(days=days)
        
        # Yangilash
        new_expiry_str = new_expiry.isoformat() if new_expiry else None
        
        async with get_db() as db:
            await db.execute(
                "UPDATE users SET premium_status = ?, premium_expiry = ? WHERE user_id = ?",
                ('approved', new_expiry_str, user_id)
            )
            await db.commit()
        
        # Admin notified flag ni reset qilish
        await self._reset_admin_notified(user_id)
        
        expiry_text = self._format_expiry(new_expiry)
        logger.info(f"✅ Premium extended: {user_id} +{duration} ({expiry_text})")
        
        return True, f"Premium {duration} ga uzaytirildi. {expiry_text}", new_expiry
        
    except Exception as e:
        logger.error(f"❌ extend_premium error {user_id}: {e}")
        return False, f"Xatolik: {str(e)}", None


async def auto_downgrade_expired_premium(self) -> Tuple[int, List[int]]:
    """
    Muddatlari tugagan premiumlarni avtomatik downgrade qilish
    
    Returns:
        Tuple[int, List[int]]: (downgrade qilinganlar soni, user_id lar ro'yxati)
    """
    try:
        now = datetime.now().isoformat()
        downgraded_users = []
        
        from bot.database.base import get_db
        
        async with get_db() as db:
            cursor = await db.execute("""
                SELECT user_id 
                FROM users 
                WHERE premium_status = 'approved' 
                AND premium_expiry IS NOT NULL 
                AND premium_expiry < ?
            """, (now,))
            
            expired_users = await cursor.fetchall()
            
            for user in expired_users:
                user_id = user['user_id']
                
                await db.execute("""
                    UPDATE users 
                    SET premium_status = 'expired'
                    WHERE user_id = ?
                """, (user_id,))
                
                downgraded_users.append(user_id)
                logger.info(f"⏰ Premium expired: {user_id}")
            
            await db.commit()
        
        count = len(downgraded_users)
        if count > 0:
            logger.info(f"✅ {count} premium users downgraded")
        
        return count, downgraded_users
        
    except Exception as e:
        logger.error(f"❌ auto_downgrade_expired_premium error: {e}")
        return 0, []


async def get_users_needing_reminder(self) -> List[Dict[str, Any]]:
    """
    Eslatma kerak bo'lgan premium userlarni topish
    
    Returns:
        list: Eslatma kerak bo'lgan userlar
    """
    try:
        now = datetime.now()
        users_to_notify = []
        
        from bot.database.base import get_db
        
        for days in REMINDER_DAYS:
            reminder_date = now + timedelta(days=days)
            reminder_date_str = reminder_date.strftime("%Y-%m-%d")
            
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT user_id, fullname, username, premium_expiry
                    FROM users 
                    WHERE premium_status = 'approved'
                    AND premium_expiry IS NOT NULL
                    AND DATE(premium_expiry) = ?
                    AND (admin_notified & ?) = 0
                """, (reminder_date_str, days))
                
                users = await cursor.fetchall()
                for user in users:
                    users_to_notify.append({
                        'user_id': user['user_id'],
                        'fullname': user['fullname'],
                        'username': user['username'],
                        'expiry_date': user['premium_expiry'],
                        'days_left': days
                    })
        
        return users_to_notify
        
    except Exception as e:
        logger.error(f"❌ get_users_needing_reminder error: {e}")
        return []


async def _get_expiry_str(self, user_id: int) -> Optional[str]:
    """Premium expiry string ni olish"""
    from bot.database.base import get_db
    async with get_db() as db:
        cursor = await db.execute("SELECT premium_expiry FROM users WHERE user_id = ?", (user_id,))
        result = await cursor.fetchone()
        return result['premium_expiry'] if result else None


async def _reset_admin_notified(self, user_id: int) -> bool:
    """Admin notified flag ni reset qilish"""
    from bot.database.base import get_db
    try:
        async with get_db() as db:
            await db.execute("UPDATE users SET admin_notified = 0 WHERE user_id = ?", (user_id,))
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"❌ reset_admin_notified error: {e}")
        return False


def _format_expiry(self, expiry_date: Optional[datetime]) -> str:
    """Premium tugash vaqtini formatlash"""
    if expiry_date is None:
        return "Cheksiz"
    
    remaining_days = (expiry_date - datetime.now()).days
    
    if remaining_days <= 0:
        return "Muddati tugagan"
    elif remaining_days == 1:
        return "1 kun qoldi"
    elif remaining_days < 7:
        return f"{remaining_days} kun qoldi"
    elif remaining_days < 30:
        weeks = remaining_days // 7
        return f"{weeks} hafta qoldi"
    else:
        months = remaining_days // 30
        return f"{months} oy qoldi"


premium_service = PremiumService()
