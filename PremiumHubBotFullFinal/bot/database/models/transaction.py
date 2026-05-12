"""Transaction model."""

import logging

from bot.database.base import get_db

logger = logging.getLogger(__name__)


async def init_transactions_table() -> None:
    try:
        async with get_db() as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            await db.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at)")
            
            await db.commit()
            logger.info("✅ Transactions table initialized successfully")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize transactions table: {e}")
        raise
