"""Anti-fraud model (fraud_logs, rate_limits, ip_tracking)."""

import logging

from bot.database.base import get_db

logger = logging.getLogger(__name__)


async def init_fraud_tables() -> None:
    try:
        async with get_db() as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS fraud_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    referral_user_id INTEGER,
                    action_type TEXT NOT NULL,
                    reason TEXT,
                    blocked_until TEXT,
                    created_at TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    offence_count INTEGER DEFAULT 1,
                    processed_by INTEGER,
                    processed_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (referral_user_id) REFERENCES users(user_id),
                    FOREIGN KEY (processed_by) REFERENCES users(user_id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    request_count INTEGER DEFAULT 1,
                    first_request TEXT NOT NULL,
                    last_request TEXT NOT NULL,
                    UNIQUE(user_id, action_type)
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS ip_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    request_count INTEGER DEFAULT 1,
                    is_suspicious INTEGER DEFAULT 0
                )
            """)
            
            await db.execute("CREATE INDEX IF NOT EXISTS idx_fraud_user ON fraud_logs(user_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_fraud_referral ON fraud_logs(referral_user_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_fraud_date ON fraud_logs(created_at)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_fraud_blocked ON fraud_logs(blocked_until)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_rate_limit_user ON rate_limits(user_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_ip_tracking_address ON ip_tracking(ip_address)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_ip_tracking_suspicious ON ip_tracking(is_suspicious)")
            
            await db.commit()
            logger.info("✅ Anti-fraud tables initialized successfully")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize fraud tables: {e}")
        raise
