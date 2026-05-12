"""Transaction service - business logic."""

import logging
from typing import List, Dict, Any

from bot.database.repositories.transaction_repo import transaction_repo
from bot.utils.common.timezone import now_str

logger = logging.getLogger(__name__)


class TransactionService:
    
    async def create_transaction(
        self,
        user_id: int,
        transaction_type: str,
        amount: float,
        description: str
    ) -> bool:
        timestamp = now_str()
        
        success = await transaction_repo.create(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            created_at=timestamp
        )
        
        if success:
            logger.info(f"✅ Transaction created: user={user_id}, type={transaction_type}, amount={amount}")
        
        return success
    
    async def get_user_transactions(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        return await transaction_repo.get_by_user(user_id, limit)
    
    async def get_transactions_by_type(self, transaction_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        return await transaction_repo.get_by_type(transaction_type, limit)
    
    async def get_total_count(self) -> int:
        return await transaction_repo.get_total_count()


transaction_service = TransactionService()
