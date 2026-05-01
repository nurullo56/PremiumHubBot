"""
Database migrations with version control.
Optimized for production with transaction safety and type safety.
"""

import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Protocol, Callable, Awaitable

from bot.database.base import get_db

logger = logging.getLogger(__name__)


# ===================== TYPES & PROTOCOLS =====================

class MigrationVersion(IntEnum):
    """Migration version enum for type safety."""
    V1_VIP_STATUS = 1
    V2_CHANNEL_DESC = 2
    V3_PREMIUM_EXPIRY = 3
    V4_LAST_PHONE_UPDATE = 4
    V5_MILESTONE_NOTIFIED = 5
    V6_FIRST_PURCHASE_BONUS = 6
    V7_BALANCE_SCALING = 7


CURRENT_VERSION = MigrationVersion.V7_BALANCE_SCALING


@dataclass(frozen=True)
class MigrationResult:
    """Migration execution result."""
    success: bool
    version: int
    description: str
    error: str | None = None


@dataclass(frozen=True)
class MigrationStatus:
    """Current migration system status."""
    current_version: int
    total_migrations: int
    pending_count: int
    is_up_to_date: bool


class MigrationFunc(Protocol):
    """Protocol for migration functions."""
    async def __call__(self) -> bool: ...


@dataclass(frozen=True)
class Migration:
    """Migration definition."""
    version: MigrationVersion
    description: str
    func: MigrationFunc


# ===================== SCHEMA HELPERS =====================

class SchemaValidator:
    """Safe schema validation and modification."""
    
    @staticmethod
    async def column_exists(table: str, column: str) -> bool:
        """Check if column exists in table."""
        # SQLite PRAGMA safe dan injection - parametrlashtirilmaydi
        # Lekin biz table nomini qattiq kontrolda tutamiz
        if not table.isidentifier() or not column.isidentifier():
            raise ValueError(f"Invalid table or column name: {table}.{column}")
        
        async with get_db() as db:
            cursor = await db.execute(f"PRAGMA table_info({table})")
            columns = {row['name'] for row in await cursor.fetchall()}
            return column in columns
    
    @staticmethod
    async def table_exists(table: str) -> bool:
        """Check if table exists."""
        if not table.isidentifier():
            raise ValueError(f"Invalid table name: {table}")
        
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (table,)
            )
            return await cursor.fetchone() is not None
    
    @staticmethod
    async def add_column(
        table: str,
        column: str,
        column_type: str,
        default: str | int | None = None
    ) -> None:
        """Add column if not exists."""
        if await SchemaValidator.column_exists(table, column):
            logger.debug(f"Column {table}.{column} already exists")
            return
        
        default_clause = f" DEFAULT {default}" if default is not None else ""
        query = f"ALTER TABLE {table} ADD COLUMN {column} {column_type}{default_clause}"
        
        async with get_db() as db:
            await db.execute(query)
            await db.commit()
        
        logger.info(f"Added column {table}.{column}")
    
    @staticmethod
    async def create_index(name: str, table: str, columns: str) -> None:
        """Create index if not exists."""
        async with get_db() as db:
            await db.execute(
                f"CREATE INDEX IF NOT EXISTS {name} ON {table}({columns})"
            )
            await db.commit()


# ===================== MIGRATION REGISTRY =====================

async def init_migrations_table() -> None:
    """Initialize migrations tracking table."""
    async with get_db() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL UNIQUE,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                checksum TEXT
            )
        """)
        await db.commit()


async def get_current_version() -> int:
    """Get current database version."""
    try:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT COALESCE(MAX(version), 0) FROM migrations"
            )
            row = await cursor.fetchone()
            return row[0] if row else 0
    except Exception as e:
        logger.error(f"Failed to get current version: {e}")
        return 0


async def mark_applied(version: int, description: str) -> None:
    """Mark migration as applied."""
    async with get_db() as db:
        await db.execute(
            "INSERT INTO migrations (version, description) VALUES (?, ?)",
            (version, description)
        )
        await db.commit()


# ===================== MIGRATIONS =====================

async def migration_v1() -> bool:
    """Add vip_status column."""
    await SchemaValidator.add_column("users", "vip_status", "INTEGER", 0)
    return True


async def migration_v2() -> bool:
    """Add channel description."""
    await SchemaValidator.add_column("channels", "description", "TEXT")
    return True


async def migration_v3() -> bool:
    """Add premium expiry."""
    await SchemaValidator.add_column("users", "premium_expiry", "TEXT")
    return True


async def migration_v4() -> bool:
    """Add last phone update tracking."""
    await SchemaValidator.add_column("users", "last_phone_update", "TEXT")
    return True


async def migration_v5() -> bool:
    """Add milestone notification tracking."""
    await SchemaValidator.add_column("users", "milestone_notified", "TEXT")
    return True


async def migration_v6() -> bool:
    """Add first purchase bonus tracking."""
    await SchemaValidator.add_column("users", "first_purchase_bonus_given", "INTEGER", 0)
    return True


async def migration_v7() -> bool:
    """Balance scaling system with outbox pattern."""
    async with get_db() as db:
        # Users table
        await SchemaValidator.add_column("users", "balance_scaled", "INTEGER", 0)
        await SchemaValidator.add_column("users", "referral_bonus_given", "INTEGER", 0)
        
        # Migrate existing balances
        await db.execute("""
            UPDATE users 
            SET balance_scaled = CAST(COALESCE(balance, 0) * 100 AS INTEGER)
            WHERE balance_scaled = 0
        """)
        
        # Balance history table
        await SchemaValidator.add_column("balance_history", "amount_scaled", "INTEGER")
        await SchemaValidator.add_column("balance_history", "new_balance_scaled", "INTEGER")
        
        # Migrate balance history
        await db.execute("""
            UPDATE balance_history 
            SET amount_scaled = CAST(COALESCE(amount, 0) * 100 AS INTEGER)
            WHERE amount_scaled IS NULL
        """)
        
        await db.execute("""
            UPDATE balance_history 
            SET new_balance_scaled = CAST(COALESCE(new_balance, 0) * 100 AS INTEGER)
            WHERE new_balance_scaled IS NULL
        """)
        
        # Create outbox table
        if not await SchemaValidator.table_exists("outbox"):
            await db.execute("""
                CREATE TABLE outbox (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    processed INTEGER DEFAULT 0,
                    processed_at TEXT,
                    retry_count INTEGER DEFAULT 0
                )
            """)
        
        # Indexes
        await SchemaValidator.create_index("idx_users_balance_scaled", "users", "balance_scaled")
        await SchemaValidator.create_index("idx_users_referral_bonus", "users", "referral_bonus_given")
        await SchemaValidator.create_index("idx_outbox_processed", "outbox", "processed, created_at")
        await SchemaValidator.create_index("idx_outbox_event_type", "outbox", "event_type")
        
        await db.commit()
    
    return True


# ===================== REGISTRY =====================

MIGRATIONS: list[Migration] = [
    Migration(MigrationVersion.V1_VIP_STATUS, "Add VIP status tracking", migration_v1),
    Migration(MigrationVersion.V2_CHANNEL_DESC, "Add channel descriptions", migration_v2),
    Migration(MigrationVersion.V3_PREMIUM_EXPIRY, "Add premium expiry tracking", migration_v3),
    Migration(MigrationVersion.V4_LAST_PHONE_UPDATE, "Add phone update tracking", migration_v4),
    Migration(MigrationVersion.V5_MILESTONE_NOTIFIED, "Add milestone notifications", migration_v5),
    Migration(MigrationVersion.V6_FIRST_PURCHASE_BONUS, "Add first purchase bonus", migration_v6),
    Migration(MigrationVersion.V7_BALANCE_SCALING, "Balance scaling with outbox", migration_v7),
]


# ===================== EXECUTION =====================

async def run_migrations() -> tuple[int, list[str]]:
    """
    Run all pending migrations with transaction safety.
    
    Returns:
        (applied_count, errors)
    """
    await init_migrations_table()
    
    current = await get_current_version()
    applied = 0
    errors: list[str] = []
    
    logger.info(f"Current version: v{current}")
    
    for migration in MIGRATIONS:
        if migration.version <= current:
            continue
        
        logger.info(f"Applying v{migration.version}: {migration.description}")
        
        try:
            # Execute migration
            success = await migration.func()
            
            if not success:
                err = f"Migration v{migration.version} returned False"
                errors.append(err)
                logger.error(err)
                break  # Stop on first failure
            
            # Mark as applied
            await mark_applied(migration.version, migration.description)
            applied += 1
            logger.info(f"✓ v{migration.version} applied")
            
        except Exception as e:
            err = f"Migration v{migration.version} failed: {e}"
            errors.append(err)
            logger.exception(err)
            break  # Stop on first error
    
    if applied:
        logger.info(f"Applied {applied} migration(s)")
    else:
        logger.info("No pending migrations")
    
    return applied, errors


async def get_status() -> MigrationStatus:
    """Get current migration status."""
    current = await get_current_version()
    total = len(MIGRATIONS)
    pending = sum(1 for m in MIGRATIONS if m.version > current)
    
    return MigrationStatus(
        current_version=current,
        total_migrations=total,
        pending_count=pending,
        is_up_to_date=(current >= int(CURRENT_VERSION))
    )


# ===================== EXPORT =====================

__all__ = [
    "run_migrations",
    "get_status",
    "get_current_version",
    "CURRENT_VERSION",
    "MigrationStatus",
]