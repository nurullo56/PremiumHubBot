"""Referral service - business logic."""

import logging
from typing import Optional, List, Dict, Any
from decimal import Decimal

from bot.database.repositories.referral_repo import referral_repo
from bot.database.repositories.user_repo import user_repo
from bot.database.repositories.referral_bonus_repo import (
    give_referral_bonus,
    get_active_referrals_count,
)
from bot.services.finance.balance_service import balance_service
from bot.config.constants import BONUS_AMOUNT, TRANSACTION_REFERRAL_BONUS
from bot.config import settings

logger = logging.getLogger(__name__)


class ReferralService:
    
    async def get_referrer(self, user_id: int) -> Optional[int]:
        return await referral_repo.get_referrer(user_id)
    
    async def get_referral_count(self, user_id: int) -> int:
        return await referral_repo.get_referral_count(user_id)
    
    async def get_referred_users(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        return await referral_repo.get_referred_users(user_id, limit)
    
    async def add_referral(self, referrer_id: int, new_user_id: int) -> bool:
        if referrer_id == new_user_id:
            logger.warning(f"❌ Self-referral attempt: {referrer_id}")
            return False
        
        referrer = await user_repo.get_by_id(referrer_id)
        if not referrer:
            logger.warning(f"❌ Referrer not found: {referrer_id}")
            return False
        
        success = await referral_repo.increment_referral_count(referrer_id)
        
        if success:
            logger.info(f"✅ Referral added: referrer={referrer_id}, new_user={new_user_id}")
        
        return success
    
    async def give_referral_bonus(self, user_id: int, referrer_id: int) -> bool:
        user = await user_repo.get_by_id(user_id)
        if not user:
            return False
        
        if user.get('referral_bonus_given'):
            logger.info(f"⚠️ Bonus already given to referrer of user {user_id}")
            return False
        
        bonus_amount = Decimal(str(BONUS_AMOUNT))
        success, _, _ = await balance_service.add_balance(
            user_id=referrer_id,
            amount=bonus_amount,
            description=f"Referral bonusi (user {user_id})",
            transaction_type=TRANSACTION_REFERRAL_BONUS
        )
        
        if success:
            await referral_repo.mark_bonus_given(user_id)
            logger.info(f"✅ Referral bonus given: referrer={referrer_id}, amount={bonus_amount}")
        
        return success
    
    async def get_top_referrers(self, limit: int = 10) -> List[Dict[str, Any]]:
        return await referral_repo.get_top_referrers(limit)
    
    async def get_total_referrals(self) -> int:
        return await referral_repo.get_total_referrals()



    async def process_bonus(self, user_id: int, fullname: str, bot) -> bool:
        """Process referral bonus."""
        try:
            user = await user_repo.get_by_id(user_id)
            if not user or not user.get('referred_by'):
                return False

            referrer_id = user['referred_by']
            success, _ = await give_referral_bonus(referrer_id, user_id, fullname, bot)
            return success
        except Exception as e:
            logger.error(f"❌ Process bonus error: {e}")
            return False

    async def get_status(self, user_id: int) -> dict:
        """Get referral status."""
        try:
            count = await get_active_referrals_count(user_id)
            required = settings.required_referrals
            remaining = max(required - count, 0)
            percent = min(int(count / required * 100), 100)

            return {
                'count': count,
                'link': f"https://t.me/{settings.bot_username}?start={user_id}",
                'remaining': remaining,
                'percent': percent
            }
        except Exception as e:
            logger.error(f"❌ Get status error: {e}")
            return {'count': 0, 'link': '', 'remaining': 5, 'percent': 0}

    async def get_friends_list(self, user_id: int, limit: int = 20) -> list:
        """Get friends list."""
        friends = await self.get_referred_users(user_id, limit)
        return [
            {
                'user_id': f['user_id'],
                'fullname': f['fullname'],
                'username': f.get('username'),
                'created_at': f.get('registration_date')
            }
            for f in friends
        ]

referral_service = ReferralService()
