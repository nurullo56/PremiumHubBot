# bot/database/repositories/referral_bonus_repo.py
"""
YANGI REFERRAL BONUS TIZIMI (1.4 olmos)
✅ To'liq versiya
"""
import logging
from decimal import Decimal
from typing import Tuple, Optional, Dict, Any, List

from bot.database.base import get_db
from bot.database.repositories.balance_repo import balance_repo
from bot.config.constants import BONUS_AMOUNT

logger = logging.getLogger(__name__)


# ===================== KONSTANTALAR =====================

REFERRAL_BONUS_AMOUNT = Decimal(str(BONUS_AMOUNT))
REFERRAL_BONUS_FLOAT = BONUS_AMOUNT


# ===================== ASOSIY FUNKSIYALAR =====================

async def give_referral_bonus(
    referrer_id: int, 
    new_user_id: int, 
    fullname: str, 
    bot=None
) -> Tuple[bool, str]:
    """
    Referral bonus berish (1.4 olmos)
    
    Args:
        referrer_id: Taklif qilgan user
        new_user_id: Yangi user
        fullname: Yangi user ismi
        bot: Bot instance (xabar yuborish uchun)
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        async with get_db() as db:
            # Bonus allaqachon berilganmi?
            cursor = await db.execute(
                "SELECT referral_bonus_given FROM users WHERE user_id = ?",
                (new_user_id,)
            )
            result = await cursor.fetchone()
            
            if result and result['referral_bonus_given']:
                logger.info(f"⚠️ Bonus allaqachon berilgan: {new_user_id}")
                return False, "Bonus allaqachon berilgan"
            
            # Referrer mavjudligini tekshirish
            cursor = await db.execute(
                "SELECT fullname, is_blocked FROM users WHERE user_id = ?",
                (referrer_id,)
            )
            referrer = await cursor.fetchone()
            
            if not referrer:
                logger.warning(f"⚠️ Referrer topilmadi: {referrer_id}")
                return False, "Referrer topilmadi"
            
            if referrer['is_blocked']:
                logger.warning(f"⚠️ Referrer bloklangan: {referrer_id}")
                return False, "Siz bloklangansiz"
            
            # Bonus berish
            success, new_balance = await balance_repo.add_balance(
                referrer_id, 
                REFERRAL_BONUS_AMOUNT
            )
            
            if not success:
                logger.error(f"❌ Balans qo'shishda xatolik: {referrer_id}")
                return False, "Balans qo'shishda xatolik"
            
            # Bonus berilganligini belgilash
            await db.execute(
                "UPDATE users SET referral_bonus_given = 1 WHERE user_id = ?",
                (new_user_id,)
            )
            
            # Referral count ni oshirish
            await db.execute("""
                UPDATE users 
                SET referral_count = COALESCE(referral_count, 0) + 1 
                WHERE user_id = ?
            """, (referrer_id,))
            
            await db.commit()
            
            logger.info(f"✅ Referral bonus berildi: {referrer_id} <- {new_user_id} (+{REFERRAL_BONUS_AMOUNT}💎)")
            
            # Xabar yuborish (agar bot berilgan bo'lsa)
            if bot:
                try:
                    from bot.data.bonus_messages import get_random_bonus_message
                    message_text = get_random_bonus_message(fullname)
                    await bot.send_message(referrer_id, message_text, parse_mode="HTML")
                    logger.info(f"✅ Xabar yuborildi: {referrer_id}")
                except Exception as e:
                    logger.error(f"❌ Xabar yuborishda xato: {e}")
            
            return True, f"+{REFERRAL_BONUS_AMOUNT}💎 bonus olmadingiz!"
            
    except Exception as e:
        logger.error(f"❌ Referral bonus berishda xatolik: {e}", exc_info=True)
        return False, f"Xatolik: {str(e)}"


async def check_bonus_given(user_id: int) -> bool:
    """
    Bonus berilganligini tekshirish
    
    Args:
        user_id: User ID
    
    Returns:
        bool: True - bonus berilgan
    """
    try:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT referral_bonus_given FROM users WHERE user_id = ?",
                (user_id,)
            )
            result = await cursor.fetchone()
            return bool(result['referral_bonus_given']) if result else False
    except Exception as e:
        logger.error(f"❌ Bonus tekshirishda xatolik {user_id}: {e}")
        return False


async def reset_bonus_flag(user_id: int) -> bool:
    """
    Bonus flag ni reset qilish
    
    Args:
        user_id: User ID
    
    Returns:
        bool: Muvaffaqiyat
    """
    try:
        async with get_db() as db:
            await db.execute(
                "UPDATE users SET referral_bonus_given = 0 WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
            logger.info(f"✅ Bonus flag reset: {user_id}")
            return True
    except Exception as e:
        logger.error(f"❌ Bonus flag reset xatolik {user_id}: {e}")
        return False


async def get_active_referrals_count(user_id: int) -> int:
    """
    Foydalanuvchining haqiqiy referallari soni (bonus berilganlar)
    
    Args:
        user_id: User ID
    
    Returns:
        int: Referallar soni
    """
    try:
        async with get_db() as db:
            cursor = await db.execute("""
                SELECT COUNT(*) AS cnt
                FROM users
                WHERE referred_by = ? AND referral_bonus_given = 1
            """, (user_id,))
            row = await cursor.fetchone()
            return row["cnt"] if row else 0
    except Exception as e:
        logger.error(f"❌ get_active_referrals_count error {user_id}: {e}")
        return 0


async def get_weekly_referrals_count(user_id: int) -> int:
    """
    Haftalik referallar soni
    
    Args:
        user_id: User ID
    
    Returns:
        int: Haftalik referallar soni
    """
    try:
        from datetime import datetime, timedelta
        now = datetime.now()
        week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        
        async with get_db() as db:
            cursor = await db.execute("""
                SELECT COUNT(*) AS cnt
                FROM users
                WHERE referred_by = ?
                  AND referral_bonus_given = 1
                  AND registration_date >= ?
            """, (user_id, week_ago))
            row = await cursor.fetchone()
            return row["cnt"] if row else 0
    except Exception as e:
        logger.error(f"❌ get_weekly_referrals_count error {user_id}: {e}")
        return 0


async def get_monthly_referrals_count(user_id: int) -> int:
    """
    Oylik referallar soni
    
    Args:
        user_id: User ID
    
    Returns:
        int: Oylik referallar soni
    """
    try:
        from datetime import datetime, timedelta
        now = datetime.now()
        month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        
        async with get_db() as db:
            cursor = await db.execute("""
                SELECT COUNT(*) AS cnt
                FROM users
                WHERE referred_by = ?
                  AND referral_bonus_given = 1
                  AND registration_date >= ?
            """, (user_id, month_ago))
            row = await cursor.fetchone()
            return row["cnt"] if row else 0
    except Exception as e:
        logger.error(f"❌ get_monthly_referrals_count error {user_id}: {e}")
        return 0


async def get_total_referral_bonus_earned(user_id: int) -> float:
    """
    Foydalanuvchi jami qancha referral bonus topgani
    
    Args:
        user_id: User ID
    
    Returns:
        float: Jami bonus miqdori
    """
    try:
        count = await get_active_referrals_count(user_id)
        return count * REFERRAL_BONUS_FLOAT
    except Exception as e:
        logger.error(f"❌ get_total_referral_bonus_earned error {user_id}: {e}")
        return 0.0


async def get_referral_stats(user_id: int) -> Dict[str, Any]:
    """
    Foydalanuvchining referral statistikasi
    
    Args:
        user_id: User ID
    
    Returns:
        dict: {
            'total': int,
            'weekly': int,
            'monthly': int,
            'total_bonus': float
        }
    """
    try:
        total = await get_active_referrals_count(user_id)
        weekly = await get_weekly_referrals_count(user_id)
        monthly = await get_monthly_referrals_count(user_id)
        total_bonus = await get_total_referral_bonus_earned(user_id)
        
        return {
            'total': total,
            'weekly': weekly,
            'monthly': monthly,
            'total_bonus': total_bonus
        }
    except Exception as e:
        logger.error(f"❌ get_referral_stats error {user_id}: {e}")
        return {
            'total': 0,
            'weekly': 0,
            'monthly': 0,
            'total_bonus': 0.0
        }


async def get_top_referrers_by_bonus(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Eng ko'p referral bonus topgan foydalanuvchilar
    
    Args:
        limit: Nechta
    
    Returns:
        list: Top referrerlar
    """
    try:
        async with get_db() as db:
            cursor = await db.execute("""
                SELECT 
                    u.user_id,
                    u.username,
                    u.fullname,
                    COUNT(r.user_id) as referral_count,
                    COUNT(r.user_id) * ? as total_bonus
                FROM users u
                LEFT JOIN users r ON r.referred_by = u.user_id AND r.referral_bonus_given = 1
                GROUP BY u.user_id, u.username, u.fullname
                HAVING COUNT(r.user_id) > 0
                ORDER BY referral_count DESC
                LIMIT ?
            """, (REFERRAL_BONUS_FLOAT, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ get_top_referrers_by_bonus error: {e}")
        return []


# ===================== EXPORT =====================

__all__ = [
    'REFERRAL_BONUS_AMOUNT',
    'REFERRAL_BONUS_FLOAT',
    'give_referral_bonus',
    'check_bonus_given',
    'reset_bonus_flag',
    'get_active_referrals_count',
    'get_weekly_referrals_count',
    'get_monthly_referrals_count',
    'get_total_referral_bonus_earned',
    'get_referral_stats',
    'get_top_referrers_by_bonus'
]