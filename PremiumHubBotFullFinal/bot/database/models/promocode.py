"""Promocode model."""

import logging

from bot.database.base import get_db

logger = logging.getLogger(__name__)


async def init_promocodes_table() -> None:
    try:
        async with get_db() as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS promocodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    fullname TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    product_price REAL NOT NULL,
                    is_used INTEGER DEFAULT 0,
                    used_by INTEGER,
                    created_date TEXT NOT NULL,
                    used_date TEXT,
                    expiry_date TEXT,
                    usage_limit INTEGER DEFAULT 1,
                    usage_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (used_by) REFERENCES users(user_id)
                )
            """)
            
            await db.execute("CREATE INDEX IF NOT EXISTS idx_promocodes_code ON promocodes(code)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_promocodes_user ON promocodes(user_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_promocodes_used ON promocodes(is_used)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_promocodes_expiry ON promocodes(expiry_date)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_promocodes_created ON promocodes(created_date)")
            
            await db.commit()
            logger.info("✅ Promocodes table initialized successfully")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize promocodes table: {e}")
        raise
