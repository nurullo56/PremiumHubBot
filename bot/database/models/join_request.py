"""Join request model (managed_chats + join_requests tables)."""

import logging

from bot.database.base import get_db

logger = logging.getLogger(__name__)


async def init_join_request_tables() -> None:
    try:
        async with get_db() as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS managed_chats (
                    chat_id TEXT PRIMARY KEY,
                    fullname TEXT NOT NULL,
                    chat_type TEXT NOT NULL,
                    invite_link TEXT,
                    added_date TEXT NOT NULL,
                    added_by INTEGER,
                    is_active INTEGER DEFAULT 1,
                    description TEXT,
                    member_count INTEGER DEFAULT 0,
                    last_checked TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS join_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    chat_id TEXT,
                    has_requested INTEGER DEFAULT 0,
                    request_date TEXT,
                    approved_date TEXT,
                    rejected_date TEXT,
                    status TEXT DEFAULT 'pending',
                    processed_by INTEGER,
                    processed_date TEXT,
                    UNIQUE(user_id, chat_id)
                )
            """)
            
            await db.execute("CREATE INDEX IF NOT EXISTS idx_managed_chats_active ON managed_chats(is_active)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_managed_chats_type ON managed_chats(chat_type)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_join_requests_user ON join_requests(user_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_join_requests_chat ON join_requests(chat_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_join_requests_status ON join_requests(status)")
            
            await db.commit()
            logger.info("✅ Join request tables initialized successfully")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize join_request tables: {e}")
        raise
