"""Fraud detection service - business logic."""

import logging
from typing import Optional

from bot.database.repositories.fraud_repo import fraud_repo
from bot.utils.common.timezone import now_str

logger = logging.getLogger(__name__)


class FraudService:
    
    async def log_suspicious_activity(
        self,
        user_id: int,
        action_type: str,
        reason: str,
        referral_user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        timestamp = now_str()
        return await fraud_repo.log_fraud(
            user_id=user_id,
            action_type=action_type,
            reason=reason,
            created_at=timestamp,
            referral_user_id=referral_user_id,
            ip_address=ip_address
        )
    
    async def check_rate_limit(self, user_id: int, action_type: str, max_requests: int, time_window_minutes: int) -> bool:
        from datetime import datetime, timedelta

        rate_limit = await fraud_repo.get_rate_limit(user_id, action_type)

        if not rate_limit:
            timestamp = now_str()
            await fraud_repo.update_rate_limit(user_id, action_type, timestamp)
            return True

        first_request = datetime.fromisoformat(rate_limit['first_request'])
        request_count = rate_limit['request_count']

        # Use now_str() as the authoritative "now" so the comparison always
        # uses the same timezone as the stored timestamp (Uzbekistan UTC+5).
        now = datetime.fromisoformat(now_str())
        time_diff = now - first_request

        if time_diff > timedelta(minutes=time_window_minutes):
            timestamp = now_str()
            await fraud_repo.update_rate_limit(user_id, action_type, timestamp)
            return True

        if request_count >= max_requests:
            logger.warning(f"⚠️ Rate limit exceeded: user={user_id}, action={action_type}")
            return False

        timestamp = now_str()
        await fraud_repo.update_rate_limit(user_id, action_type, timestamp)
        return True


fraud_service = FraudService()
