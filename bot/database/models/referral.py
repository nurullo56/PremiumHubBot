"""Referral model - logic stored in users table."""

import logging

logger = logging.getLogger(__name__)


async def init_referral_table() -> None:
    """
    Referral data stored in users table:
    - referral_count
    - referred_by
    - bonus_status
    - referral_bonus_given
    """
    logger.info("✅ Referral logic uses users table")
