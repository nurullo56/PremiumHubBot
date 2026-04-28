"""Premium model - logic stored in users table."""

import logging

logger = logging.getLogger(__name__)


async def init_premium_table() -> None:
    """
    Premium data stored in users table:
    - premium_status
    - premium_expiry
    - admin_notified
    - vip_status
    """
    logger.info("✅ Premium logic uses users table")
