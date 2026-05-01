"""
Database migrations with version control.
Optimized for production with transaction safety and type safety.
"""

import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import Protocol

import aiosqlite

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
    """
    Safe schema validation and modification.

    All methods accept an open `db` connection so that callers can share a
    single connection/transaction — avoiding nested get_db() calls that cause
    "database is locked" when multiple connections compete for a write lock.
    """

    @staticmethod
    def _validate_identifier(table: str, column: str | None = None) -> None:
        if not table.isidentifier():
            raise ValueError(f"Invalid table name: {table}")
        if column is not None and not column.isidentifier():
            raise ValueError(f"Invalid column name: {column}")

    @staticmethod
    async def column_exists(db: aiosqlite.Connection, table: str, column: str) -> bool:
        SchemaValidator._validate_identifier(table, column)
        cursor = await db.execute(f"PRAGMA table_info({table})")
        columns = {row['name'] for row in await cursor.fetchall()}
        return column in columns

    @staticmethod
    async def table_exists(db: aiosqlite.Connection, table: str) -> bool:
        SchemaValidator._validate_identifier(table)
        cursor = await db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        )
        return await cursor.fetchone() is not None

    @staticmethod
    async def add_column(
        db: aiosqlite.Connection,
        table: str,
        column: str,
        column_type: str,
        default: str | int | None = None,
    ) -> None:
        """Add column if it does not already exist (no implicit commit)."""
        if await SchemaValidator.column_exists(db, table, column):
            logger.debug(f"Column {table}.{column} already exists — skipping")
            return
        default_clause = f" DEFAULT {default}" if default is not None else ""
        await db.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {column_type}{default_clause}"
        )
        logger.info(f"Added column {table}.{column}")

    @staticmethod
    async def create_index(
        db: aiosqlite.Connection, name: str, table: str, columns: str
    ) -> None:
        """Create index if not exists (no implicit commit)."""
        await db.execute(
            f"CREATE INDEX IF NOT EXISTS {name} ON {table}({columns})"
        )


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
    async with get_db() as db:
        await SchemaValidator.add_column(db, "users", "vip_status", "INTEGER", 0)
        await db.commit()
    return True


async def migration_v2() -> bool:
    async with get_db() as db:
        await SchemaValidator.add_column(db, "channels", "description", "TEXT")
        await db.commit()
    return True


async def migration_v3() -> bool:
    async with get_db() as db:
        await SchemaValidator.add_column(db, "users", "premium_expiry", "TEXT")
        await db.commit()
    return True


async def migration_v4() -> bool:
    async with get_db() as db:
        await SchemaValidator.add_column(db, "users", "last_phone_update", "TEXT")
        await db.commit()
    return True


async def migration_v5() -> bool:
    async with get_db() as db:
        await SchemaValidator.add_column(db, "users", "milestone_notified", "TEXT")
        await db.commit()
    return True


async def migration_v6() -> bool:
    async with get_db() as db:
        await SchemaValidator.add_column(db, "users", "first_purchase_bonus_given", "INTEGER", 0)
        await db.commit()
    return True


async def migration_v7() -> bool:
    """Balance scaling system + outbox pattern. One connection, one transaction."""
    async with get_db() as db:
        # --- users ---
        await SchemaValidator.add_column(db, "users", "balance_scaled", "INTEGER", 0)
        await SchemaValidator.add_column(db, "users", "referral_bonus_given", "INTEGER", 0)

        await db.execute("""
            UPDATE users
            SET balance_scaled = CAST(COALESCE(balance, 0) * 100 AS INTEGER)
            WHERE balance_scaled = 0
        """)

        # --- balance_history ---
        await SchemaValidator.add_column(db, "balance_history", "amount_scaled", "INTEGER")
        await SchemaValidator.add_column(db, "balance_history", "new_balance_scaled", "INTEGER")

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

        # --- outbox ---
        if not await SchemaValidator.table_exists(db, "outbox"):
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

        # --- indexes ---
        await SchemaValidator.create_index(db, "idx_users_balance_scaled", "users", "balance_scaled")
        await SchemaValidator.create_index(db, "idx_users_referral_bonus", "users", "referral_bonus_given")
        await SchemaValidator.create_index(db, "idx_outbox_processed", "outbox", "processed, created_at")
        await SchemaValidator.create_index(db, "idx_outbox_event_type", "outbox", "event_type")

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