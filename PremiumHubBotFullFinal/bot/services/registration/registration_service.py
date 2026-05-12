# bot/services/registration/registration_service.py - TO'LIQ VERSIYA

"""Registration service for user registration flow."""

import logging
from typing import Optional, Tuple

from bot.database.repositories.user_repo import user_repo
from bot.services.referral.referral_service import referral_service
from bot.services.channel.channel_service import channel_service
from bot.config import settings

logger = logging.getLogger(__name__)


class RegistrationService:
    """Service for managing user registration flow."""
    
    def __init__(self):
        self.user_repo = user_repo
    
    async def is_registration_complete(self, user_id: int) -> bool:
        """
        Check if user completed all registration steps.
        
        Returns:
            bool: True if registration is complete, False otherwise
        """
        user = await self.user_repo.get_by_id(user_id)
        
        if not user:
            return False
        
        # Check captcha
        if not user.get('captcha_passed') and not settings.test_mode:
            logger.debug(f"User {user_id} missing captcha")
            return False
        
        # Check gender
        if not user.get('gender'):
            logger.debug(f"User {user_id} missing gender")
            return False
        
        # Check phone
        if not user.get('phone'):
            logger.debug(f"User {user_id} missing phone")
            return False
        
        # Check subscription (if there are active channels)
        channels = await channel_service.get_active_channels()
        if channels and not user.get('is_subscribed'):
            logger.debug(f"User {user_id} missing subscription")
            return False
        
        return True
    
    async def get_next_step(self, user_id: int) -> Optional[str]:
        """
        Get the next registration step for user.
        
        Returns:
            str or None: 'captcha', 'gender', 'phone', 'subscription', or None if complete
        """
        user = await self.user_repo.get_by_id(user_id)
        
        if not user:
            return None
        
        if not user.get('captcha_passed') and not settings.test_mode:
            return 'captcha'
        
        if not user.get('gender'):
            return 'gender'
        
        if not user.get('phone'):
            return 'phone'
        
        channels = await channel_service.get_active_channels()
        if channels and not user.get('is_subscribed'):
            return 'subscription'
        
        return None
    
    async def complete_registration(self, user_id: int, referred_by: Optional[int] = None) -> bool:
        """
        Complete registration and give referral bonuses.
        
        Args:
            user_id: User ID
            referred_by: Referrer ID (if any)
        
        Returns:
            bool: True if successful
        """
        try:
            # Update user as registered
            await self.user_repo.update(user_id, {
                'is_registered': True,
                'last_activity': None
            })
            
            # Give welcome bonus
            from bot.services.finance.balance_service import balance_service
            await balance_service.add_balance(
                user_id,
                0,  # Welcome bonus amount (0 for now)
                "Ro'yxatdan o'tish bonusi"
            )
            
            logger.info(f"✅ Registration completed for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to complete registration for {user_id}: {e}")
            return False


registration_service = RegistrationService()


__all__ = ["registration_service", "RegistrationService"]