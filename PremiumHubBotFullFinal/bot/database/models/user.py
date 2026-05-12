"""User model and table initialization."""

import logging

from bot.database.base import get_db

logger = logging.getLogger(__name__)


async def init_users_table() -> None:
    """
    Initialize users table with all columns and indexes.
    
    Schema includes:
    - Basic info: user_id, username, fullname
    - Contact: phone (unique)
    - Profile: gender
    - Finance: balance
    - Referral: referral_count, referred_by, bonus_status, referral_bonus_given
    - Subscription: is_subscribed, captcha_passed
    - Premium: admin_notified, premium_status, premium_expiry, vip_status
    - Timestamps: registration_date, last_activity, last_phone_update
    - Security: failed_attempts, is_blocked
    """
    try:
        async with get_db() as db:
            # Create main table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    fullname TEXT,
                    phone TEXT UNIQUE,
                    gender TEXT,
                    balance REAL DEFAULT 0.0,
                    referral_count INTEGER DEFAULT 0,
                    referred_by INTEGER,
                    bonus_status INTEGER DEFAULT 0,
                    referral_bonus_given INTEGER DEFAULT 0,
                    is_subscribed INTEGER DEFAULT 0,
                    captcha_passed INTEGER DEFAULT 0,
                    admin_notified INTEGER DEFAULT 0,
                    premium_status TEXT DEFAULT 'none',
                    premium_expiry TEXT,
                    vip_status INTEGER DEFAULT 0,
                    registration_date TEXT,
                    last_activity TEXT,
                    last_phone_update TEXT,
                    failed_attempts INTEGER DEFAULT 0,
                    is_blocked INTEGER DEFAULT 0,
                    FOREIGN KEY (referred_by) REFERENCES users(user_id)
                )
            """)
            
            # Check existing columns for migration
            cursor = await db.execute("PRAGMA table_info(users)")
            columns = await cursor.fetchall()
            column_names = {col[1] for col in columns}
            
            # Add missing columns (migration)
            migrations = {
                'bonus_status': "ALTER TABLE users ADD COLUMN bonus_status INTEGER DEFAULT 0",
                'referral_bonus_given': "ALTER TABLE users ADD COLUMN referral_bonus_given INTEGER DEFAULT 0",
                'premium_expiry': "ALTER TABLE users ADD COLUMN premium_expiry TEXT",
                'vip_status': "ALTER TABLE users ADD COLUMN vip_status INTEGER DEFAULT 0",
                'last_phone_update': "ALTER TABLE users ADD COLUMN last_phone_update TEXT",
                'failed_attempts': "ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0",
                'is_blocked': "ALTER TABLE users ADD COLUMN is_blocked INTEGER DEFAULT 0",
            }
            
            for col_name, sql in migrations.items():
                if col_name not in column_names:
                    await db.execute(sql)
                    logger.info(f"✅ Added column '{col_name}' to users table")
            
            # Create indexes for performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
                "CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)",
                "CREATE INDEX IF NOT EXISTS idx_users_referred_by ON users(referred_by)",
                "CREATE INDEX IF NOT EXISTS idx_users_registration ON users(registration_date)",
                "CREATE INDEX IF NOT EXISTS idx_users_premium_status ON users(premium_status)",
                "CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity)",
                "CREATE INDEX IF NOT EXISTS idx_users_balance ON users(balance)",
                "CREATE INDEX IF NOT EXISTS idx_users_blocked ON users(is_blocked)",
            ]
            
            for index_sql in indexes:
                await db.execute(index_sql)
            
            await db.commit()
            logger.info("✅ Users table initialized successfully")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize users table: {e}")
        raise
