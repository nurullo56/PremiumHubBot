# bot/services/user/user_service.py
"""
User Service - Business logic layer for user operations
"""
import logging
import re
from typing import Optional, Tuple, List, Dict, Any

from bot.database.repositories.user_repo import user_repo
from bot.database.repositories.balance_repo import balance_repo
from bot.database.repositories.referral_repo import referral_repo
from bot.database.base import get_db
from bot.utils.common.timezone import now_str

logger = logging.getLogger(__name__)


# ===================== KONSTANTALAR =====================

PHONE_PATTERN = r'^\+?998[0-9]{9}$'
BONUS_AMOUNT = 5.0


# ===================== YORDAMCHI FUNKSIYALAR =====================

def validate_phone(phone: str) -> Tuple[bool, str]:
    """Telefon raqamini tekshirish"""
    if not phone:
        return False, "Telefon raqami kiritilmagan"
    
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    
    if not re.match(PHONE_PATTERN, phone_clean):
        return False, "Telefon raqami noto'g'ri formatda (+998XXXXXXXXX)"
    
    return True, "OK"


def normalize_phone(phone: str) -> str:
    """Telefon raqamini standart formatga keltirish"""
    if not phone:
        return ""
    
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 9:
        return f"+998{digits}"
    elif len(digits) == 12 and digits.startswith('998'):
        return f"+{digits}"
    elif len(digits) == 13 and digits.startswith('998'):
        return f"+{digits}"
    else:
        return phone


# ===================== USER SERVICE KLASSI =====================

class UserService:
    """User operatsiyalari uchun business logic layer"""
    
    async def get(self, user_id: int) -> Optional[Dict[str, Any]]:
        """User ma'lumotlarini olish"""
        return await user_repo.get_by_id(user_id)
    
    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Username bo'yicha user topish"""
        return await user_repo.get_by_username(username)
    
    async def get_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Telefon bo'yicha user topish"""
        return await user_repo.get_by_phone(phone)
    
    async def exists(self, user_id: int) -> bool:
        """User borligini tekshirish"""
        return await user_repo.exists(user_id)
    
    async def create(
        self,
        user_id: int,
        username: Optional[str],
        fullname: str,
        phone: Optional[str] = None,
        referred_by: Optional[int] = None
    ) -> Tuple[bool, str]:
        """Yangi user yaratish"""
        try:
            normalized_phone = None
            if phone:
                is_valid, error_msg = validate_phone(phone)
                if not is_valid:
                    return False, error_msg
                normalized_phone = normalize_phone(phone)
                
                exists, existing_id = await self.check_phone_exists(normalized_phone)
                if exists:
                    return False, "Bu telefon raqami allaqachon ishlatilgan"
            
            if referred_by:
                if not await self.exists(referred_by):
                    referred_by = None
            
            now = now_str()
            
            success = await user_repo.create(
                user_id=user_id,
                username=username,
                fullname=fullname,
                phone=normalized_phone,
                referred_by=referred_by,
                registration_date=now
            )
            
            if success:
                logger.info(f"✅ User yaratildi: {user_id}")
                return True, "Muvaffaqiyatli ro'yxatdan o'tdingiz"
            
            return False, "Xatolik yuz berdi"
            
        except Exception as e:
            logger.error(f"❌ User create error: {e}")
            return False, f"Xatolik: {str(e)}"
    
    async def update_phone(self, user_id: int, phone: str) -> Tuple[bool, str]:
        """Telefon raqamini yangilash"""
        try:
            is_valid, error_msg = validate_phone(phone)
            if not is_valid:
                return False, error_msg
            
            normalized = normalize_phone(phone)
            
            exists, existing_id = await self.check_phone_exists(normalized)
            if exists and existing_id != user_id:
                return False, "Bu telefon raqami allaqachon boshqa foydalanuvchi tomonidan ishlatilgan"
            
            now = now_str()
            success = await user_repo.update_phone(user_id, normalized, now)
            
            if success:
                logger.info(f"✅ Telefon yangilandi: {user_id} -> {normalized}")
                return True, "Telefon raqami muvaffaqiyatli yangilandi"
            
            return False, "Telefon yangilashda xatolik"
            
        except Exception as e:
            logger.error(f"❌ update_phone error: {e}")
            return False, f"Xatolik: {str(e)}"
    
    async def get_phone(self, user_id: int) -> Optional[str]:
        """Telefon raqamini olish"""
        user = await self.get(user_id)
        return user.get('phone') if user else None
    
    async def check_phone_exists(self, phone: str) -> Tuple[bool, Optional[int]]:
        """Telefon raqami mavjudligini tekshirish"""
        return await user_repo.phone_exists(normalize_phone(phone))
    
    async def update_gender(self, user_id: int, gender: str) -> bool:
        """Jinsni yangilash"""
        if gender not in ['male', 'female']:
            return False
        return await user_repo.update_gender(user_id, gender)
    
    async def get_gender(self, user_id: int) -> Optional[str]:
        """Jinsni olish"""
        user = await self.get(user_id)
        return user.get('gender') if user else None
    
    async def update_subscription(self, user_id: int, is_subscribed: bool) -> bool:
        """Obuna holatini yangilash"""
        return await user_repo.update_subscription(user_id, is_subscribed)
    
    async def is_subscribed(self, user_id: int) -> bool:
        """Obuna bo'lganligini tekshirish"""
        user = await self.get(user_id)
        return bool(user and user.get('is_subscribed'))
    
    async def update_last_activity(self, user_id: int) -> bool:
        """Oxirgi faollik vaqtini yangilash"""
        return await user_repo.update_last_activity(user_id, now_str())
    
    async def update_balance(self, user_id: int, amount: float) -> bool:
        """Balansni to'g'ridan-to'g'ri yangilash"""
        from decimal import Decimal
        return await balance_repo.set_balance(user_id, Decimal(str(amount)))
    
    async def mark_captcha_passed(self, user_id: int) -> bool:
        """Captcha o'tganligini belgilash"""
        return await user_repo.mark_captcha_passed(user_id)
    
    async def has_passed_captcha(self, user_id: int) -> bool:
        """Captcha o'tganligini tekshirish"""
        user = await self.get(user_id)
        return bool(user and user.get('captcha_passed'))
    
    async def reset_captcha(self, user_id: int) -> bool:
        """Captcha holatini reset qilish"""
        try:
            async with get_db() as db:
                await db.execute("UPDATE users SET captcha_passed = 0 WHERE user_id = ?", (user_id,))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"❌ reset_captcha error: {e}")
            return False
    
    async def has_received_bonus(self, user_id: int) -> bool:
        """Bonus olganligini tekshirish"""
        user = await self.get(user_id)
        return bool(user and user.get('bonus_status'))
    
    async def block_user(self, user_id: int, reason: str = None) -> Tuple[bool, str]:
        """Foydalanuvchini bloklash"""
        success = await user_repo.block_user(user_id)
        if success:
            logger.warning(f"🚫 User bloklandi: {user_id}")
            return True, f"Foydalanuvchi {user_id} bloklandi"
        return False, "Bloklashda xatolik"
    
    async def unblock_user(self, user_id: int) -> Tuple[bool, str]:
        """Foydalanuvchini blokdan chiqarish"""
        success = await user_repo.unblock_user(user_id)
        if success:
            logger.info(f"✅ User blokdan chiqarildi: {user_id}")
            return True, f"Foydalanuvchi {user_id} blokdan chiqarildi"
        return False, "Blokdan chiqarishda xatolik"
    
    async def is_blocked(self, user_id: int) -> bool:
        """Foydalanuvchi bloklanganmi"""
        user = await self.get(user_id)
        return bool(user and user.get('is_blocked'))
    
    async def get_total_count(self) -> int:
        """Jami userlar soni"""
        return await user_repo.get_total_count()
    
    async def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Barcha userlar"""
        return await user_repo.get_all(limit, offset)
    
    async def get_users_with_phone_count(self) -> int:
        """Telefon raqami bor userlar soni"""
        return await user_repo.get_with_phone_count()
    
    async def get_gender_counts(self) -> Tuple[int, int]:
        """Jinslar bo'yicha statistika"""
        return await user_repo.get_gender_counts()
    
    async def get_subscribed_count(self) -> int:
        """Obuna bo'lgan userlar soni"""
        return await user_repo.get_subscribed_count()
    
    async def delete_user(self, user_id: int, soft_delete: bool = True) -> Tuple[bool, str]:
        """Foydalanuvchini o'chirish"""
        if soft_delete:
            success = await user_repo.block_user(user_id)
            return success, "Foydalanuvchi bloklandi" if success else "Xatolik"
        else:
            success = await user_repo.delete_user(user_id)
            return success, "Foydalanuvchi o'chirildi" if success else "Xatolik"
    
    async def can_update_phone(self, user_id: int) -> Tuple[bool, str]:
        """Telefon yangilash mumkinligini tekshirish"""
        user = await self.get(user_id)
        if not user:
            return False, "Foydalanuvchi topilmadi"
        
        if user.get('is_blocked'):
            return False, "Akkauntingiz bloklangan"
        
        last_update = user.get('last_phone_update')
        if last_update:
            from datetime import datetime
            last_update_date = datetime.fromisoformat(last_update)
            from datetime import datetime as dt
            days_since_update = (dt.now() - last_update_date).days
            
            if days_since_update < 7:
                return False, f"Telefon raqamini oxirgi marta {days_since_update} kun oldin o'zgartirgansiz. 7 kunda faqat 1 marta o'zgartirish mumkin."
        
        return True, "OK"


# ===================== SINGLETON =====================

user_service = UserService()


__all__ = [
    'user_service',
    'UserService',
    'validate_phone',
    'normalize_phone'
]