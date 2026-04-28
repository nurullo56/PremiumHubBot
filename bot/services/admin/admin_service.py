"""Admin service - business logic."""

import logging
from typing import List, Dict, Any
from decimal import Decimal

from bot.database.repositories.user_repo import user_repo
from bot.services.finance.balance_service import balance_service
from bot.config.constants import TRANSACTION_ADMIN_ADD

logger = logging.getLogger(__name__)


class AdminService:
    
    async def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return await user_repo.get_all(limit, offset)
    
    async def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        return await user_repo.get_by_id(user_id)
    
    async def block_user(self, user_id: int) -> bool:
        success = await user_repo.block_user(user_id)
        
        if success:
            logger.warning(f"⚠️ User blocked by admin: {user_id}")
        
        return success
    
    async def unblock_user(self, user_id: int) -> bool:
        success = await user_repo.unblock_user(user_id)
        
        if success:
            logger.info(f"✅ User unblocked by admin: {user_id}")
        
        return success
    
    async def add_balance_to_user(
        self,
        user_id: int,
        amount: Decimal,
        description: str = "Admin qo'shdi"
    ) -> tuple[bool, str]:
        success, message, new_balance = await balance_service.add_balance(
            user_id=user_id,
            amount=amount,
            description=description,
            transaction_type=TRANSACTION_ADMIN_ADD
        )
        
        if success:
            logger.info(f"✅ Balance added by admin: user={user_id}, amount={amount}")
        
        return success, message
    
    async def subtract_balance_from_user(
        self,
        user_id: int,
        amount: Decimal,
        description: str = "Admin ayirdi"
    ) -> tuple[bool, str]:
        success, message, new_balance = await balance_service.subtract_balance(
            user_id=user_id,
            amount=amount,
            description=description
        )
        
        if success:
            logger.info(f"✅ Balance subtracted by admin: user={user_id}, amount={amount}")
        
        return success, message
    
    async def set_user_balance(self, user_id: int, amount: Decimal) -> bool:
        success = await balance_service.set_balance(user_id, amount)
        
        if success:
            logger.info(f"✅ Balance set by admin: user={user_id}, amount={amount}")
        
        return success


admin_service = AdminService()
