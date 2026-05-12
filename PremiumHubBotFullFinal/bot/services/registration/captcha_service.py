"""Captcha service - business logic."""

import logging
from typing import Optional

from bot.database.repositories.user_repo import user_repo

logger = logging.getLogger(__name__)


class CaptchaService:
    
    async def has_passed_captcha(self, user_id: int) -> bool:
        user = await user_repo.get_by_id(user_id)
        return user.get('captcha_passed', 0) == 1 if user else False
    
    async def mark_captcha_passed(self, user_id: int) -> bool:
        success = await user_repo.mark_captcha_passed(user_id)
        
        if success:
            logger.info(f"✅ Captcha passed: user_id={user_id}")
        
        return success
    
    async def verify_captcha(self, user_id: int, captcha_result: bool) -> bool:
        """
        Verify captcha result (WebApp sends result).
        
        Args:
            user_id: User ID
            captcha_result: True if captcha solved correctly
            
        Returns:
            bool: Success
        """
        if not captcha_result:
            logger.warning(f"⚠️ Captcha failed: user_id={user_id}")
            return False
        
        return await self.mark_captcha_passed(user_id)


captcha_service = CaptchaService()
