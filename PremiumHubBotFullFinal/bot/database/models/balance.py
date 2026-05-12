"""Balance history model."""

import logging

from bot.database.base import get_db

logger = logging.getLogger(__name__)


async def init_balance_table() -> None:
    """
    Initialize balance_history table.
    
    Tracks all balance changes:
    - Referral bonuses
    - Admin adjustments
    - Transfers
    - Purchases
    """
    try:
        async with get_db() as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS balance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    new_balance REAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Create indexes
            await db.execute("CREATE INDEX IF NOT EXISTS idx_balance_user ON balance_history(user_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_balance_type ON balance_history(transaction_type)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_balance_timestamp ON balance_history(timestamp)")
            
            await db.commit()
            logger.info("✅ Balance history table initialized successfully")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize balance_history table: {e}")
        raise
