"""Channel model."""

import logging

from bot.database.base import get_db

logger = logging.getLogger(__name__)


async def init_channels_table() -> None:
    try:
        async with get_db() as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT UNIQUE NOT NULL,
                    channel_name TEXT NOT NULL,
                    channel_url TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    description TEXT,
                    added_by INTEGER
                )
            """)
            
            await db.execute("CREATE INDEX IF NOT EXISTS idx_channels_id ON channels(channel_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_channels_active ON channels(is_active)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_channels_added_by ON channels(added_by)")
            
            await db.commit()
            logger.info("✅ Channels table initialized successfully")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize channels table: {e}")
        raise
