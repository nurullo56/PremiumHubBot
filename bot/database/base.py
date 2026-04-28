"""Database connection management with retry logic."""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import aiosqlite

from bot.config import settings
from bot.config.constants import DB_TIMEOUT, DB_MAX_RETRIES, DB_RETRY_DELAY

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Database connection failed after retries."""


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    Get database connection with retry logic.
    
    Yields:
        aiosqlite.Connection: Active database connection
        
    Raises:
        DatabaseConnectionError: If connection fails after max retries
    """
    retries = 0
    last_error = None
    
    while retries < DB_MAX_RETRIES:
        try:
            # Ensure database directory exists
            db_path = Path(settings.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect with timeout
            async with aiosqlite.connect(
                database=str(db_path),
                timeout=DB_TIMEOUT
            ) as db:
                # Enable Row factory
                db.row_factory = aiosqlite.Row
                
                # SQLite performance optimizations
                await db.execute("PRAGMA journal_mode=WAL")
                await db.execute("PRAGMA synchronous=NORMAL")
                await db.execute("PRAGMA cache_size=10000")
                await db.execute("PRAGMA temp_store=MEMORY")
                await db.execute("PRAGMA busy_timeout=30000")  # 30 seconds
                
                # Foreign keys enforcement
                await db.execute("PRAGMA foreign_keys=ON")
                
                yield db
                return  # Success - exit retry loop
                
        except aiosqlite.Error as e:
            last_error = e
            retries += 1
            
            if retries < DB_MAX_RETRIES:
                wait_time = DB_RETRY_DELAY * (2 ** (retries - 1))  # Exponential backoff
                logger.warning(
                    f"⚠️ Database connection failed (attempt {retries}/{DB_MAX_RETRIES}). "
                    f"Retrying in {wait_time:.1f}s... Error: {e}"
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    f"❌ Database connection failed after {DB_MAX_RETRIES} attempts. "
                    f"Last error: {e}"
                )
                raise DatabaseConnectionError(
                    f"Failed to connect to database after {DB_MAX_RETRIES} attempts"
                ) from last_error


async def init_database() -> None:
    """Initialize database with all tables."""
    try:
        logger.info("📦 Initializing database tables...")
        
        from bot.database.models.user import init_users_table
        from bot.database.models.channel import init_channels_table
        from bot.database.models.balance import init_balance_table
        from bot.database.models.transaction import init_transactions_table
        from bot.database.models.referral import init_referral_table
        from bot.database.models.promocode import init_promocodes_table
        from bot.database.models.premium import init_premium_table
        from bot.database.models.join_request import init_join_request_tables
        from bot.database.models.fraud import init_fraud_tables
        
        await init_users_table()
        await init_balance_table()
        await init_referral_table()
        await init_channels_table()
        await init_promocodes_table()
        await init_transactions_table()
        await init_premium_table()
        await init_join_request_tables()
        await init_fraud_tables()
        
        logger.info("✅ All database tables initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def optimize_database() -> None:
    """Optimize database (VACUUM + ANALYZE)."""
    try:
        logger.info("🔧 Optimizing database...")
        
        async with get_db() as db:
            # VACUUM requires exclusive lock - run outside transaction
            await db.execute("VACUUM")
            await db.execute("ANALYZE")
            await db.commit()
            
        logger.info("✅ Database optimized successfully")
        
    except Exception as e:
        logger.error(f"❌ Database optimization failed: {e}")
        # Non-critical error - don't raise
