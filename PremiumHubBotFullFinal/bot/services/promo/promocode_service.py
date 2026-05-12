# bot/services/promo/promocode_service.py
"""Promocode service for managing promocodes."""

import logging
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from bot.database.uow.uow import UnitOfWork

logger = logging.getLogger(__name__)


class PromocodeService:
    """Service for promocode operations."""
    
    def generate_code(self, length: int = 8) -> str:
        """Generate random promocode."""
        letters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(letters) for _ in range(length))
    
    async def create_promocode(
        self,
        user_id: int,
        product_name: str,
        product_price: float,
        expiry_days: int = 30,
        usage_limit: int = 1,
        username: Optional[str] = None,
        fullname: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Create a new promocode."""
        async with UnitOfWork() as uow:
            try:
                code = self.generate_code()
                now = datetime.now().isoformat()
                expiry = (datetime.now() + timedelta(days=expiry_days)).isoformat() if expiry_days else None

                if not fullname:
                    user = await uow.users.get_by_id(user_id)
                    fullname = user.get('fullname', 'Unknown') if user else 'Unknown'

                success = await uow.promocodes.create(
                    code=code,
                    user_id=user_id,
                    username=username,
                    fullname=fullname,
                    product_name=product_name,
                    product_price=product_price,
                    created_date=now,
                    expiry_date=expiry,
                    usage_limit=usage_limit
                )

                if not success:
                    return False, ""

            except Exception as e:
                logger.error(f"Failed to create promocode: {e}")
                return False, ""

            await uow.commit()
            logger.info(f"✅ Promocode created: {code}")
            return True, code
    
    async def use_promocode(
        self, 
        code: str, 
        user_id: int
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Use a promocode.
        
        Returns:
            Tuple[bool, str, dict]: (success, message, promocode_data)
        """
        async with UnitOfWork() as uow:
            try:
                promocode = await uow.promocodes.get_by_code(code)

                if not promocode:
                    return False, "❌ Promokod topilmadi!", None

                if promocode.get('is_used'):
                    return False, "❌ Bu promokod allaqachon ishlatilgan!", None

                if promocode.get('expiry_date'):
                    expiry = datetime.fromisoformat(promocode['expiry_date'])
                    if expiry < datetime.now():
                        return False, "❌ Promokod muddati o'tgan!", None

                usage_count = promocode.get('usage_count', 0)
                usage_limit = promocode.get('usage_limit', 1)
                if usage_count >= usage_limit:
                    return False, "❌ Promokod limiti tugagan!", None

                now = datetime.now().isoformat()
                success = await uow.promocodes.mark_used(code, user_id, now)

                if not success:
                    return False, "❌ Xatolik yuz berdi!", None

            except Exception as e:
                logger.error(f"Failed to use promocode: {e}")
                return False, f"❌ Xatolik: {str(e)}", None

            await uow.commit()
            logger.info(f"✅ Promocode used: {code} by {user_id}")
            return True, "✅ Promokod muvaffaqiyatli qo'llandi!", promocode
    
    async def get_user_promocodes(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all promocodes created by user."""
        async with UnitOfWork() as uow:
            return await uow.promocodes.get_by_user(user_id)
    
    async def get_all_promocodes(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all promocodes."""
        async with UnitOfWork() as uow:
            return await uow.promocodes.get_all(limit)
    
    async def get_unused_count(self, user_id: int) -> int:
        """Get number of unused promocodes for user."""
        async with UnitOfWork() as uow:
            return await uow.promocodes.get_unused_count(user_id)


# Singleton instance
promocode_service = PromocodeService()