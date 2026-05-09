# bot/services/referral/referral_bonus_service.py
"""Referral bonus service - first purchase bonus"""

import logging
from decimal import Decimal
from typing import Tuple, Optional

from aiogram import Bot

from bot.database.base import get_db
from bot.services.finance.balance_service import balance_service
from bot.database.repositories.user_repo import user_repo

logger = logging.getLogger(__name__)

FIRST_PURCHASE_BONUS = Decimal('10')  # 10 olmos


class ReferralBonusService:
    """Referral bonus service for first purchase bonus"""
    
    async def give_first_purchase_bonus(
        self,
        referrer_id: int,
        buyer_id: int,
        bot: Optional[Bot] = None
    ) -> Tuple[bool, Decimal]:
        """
        Do'st birinchi xarid qilganda bonus berish
        
        Args:
            referrer_id: Taklif qilgan user_id
            buyer_id: Xaridor user_id
            bot: Bot instance (ixtiyoriy, xabar yuborish uchun)
        
        Returns:
            Tuple[bool, Decimal]: (success, bonus_amount)
        """
        try:
            # Atomically claim the bonus slot: only the first concurrent call succeeds.
            # UPDATE...WHERE first_purchase_bonus_given = 0 acts as a test-and-set;
            # rowcount == 0 means another request already claimed it.
            async with get_db() as db:
                cursor = await db.execute(
                    "UPDATE users SET first_purchase_bonus_given = 1 "
                    "WHERE user_id = ? AND first_purchase_bonus_given = 0",
                    (buyer_id,)
                )
                await db.commit()
                if cursor.rowcount == 0:
                    logger.info(f"⚠️ First purchase bonus already given: {buyer_id}")
                    return False, Decimal('0')

            # Bonus berish (flag already set — safe to retry balance if it fails)
            success, _, _ = await balance_service.add_balance(
                referrer_id,
                FIRST_PURCHASE_BONUS,
                f"Birinchi xarid bonusi: user {buyer_id}"
            )

            if success:
                logger.info(f"✅ First purchase bonus: {referrer_id} +{FIRST_PURCHASE_BONUS}💎 (from {buyer_id})")
                
                # Xabar yuborish
                if bot:
                    try:
                        referrer = await user_repo.get_by_id(referrer_id)
                        buyer = await user_repo.get_by_id(buyer_id)
                        
                        if referrer and buyer:
                            buyer_name = buyer.get('fullname', 'Foydalanuvchi')
                            
                            await bot.send_message(
                                referrer_id,
                                f"🎉 <b>Qo'shimcha bonus!</b>\n\n"
                                f"👤 {buyer_name} birinchi xarid qildi!\n"
                                f"💎 +{FIRST_PURCHASE_BONUS} olmos (Bonus)\n\n"
                                f"Davom eting va ko'proq mukofotlar oling! 🚀",
                                parse_mode="HTML"
                            )
                    except Exception as e:
                        logger.error(f"⚠️ First purchase message error: {e}")
                
                return True, FIRST_PURCHASE_BONUS
            
            return False, Decimal('0')
            
        except Exception as e:
            logger.error(f"❌ give_first_purchase_bonus error: {e}")
            return False, Decimal('0')


referral_bonus_service = ReferralBonusService()