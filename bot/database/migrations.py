# bot/database/migrations.py
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

from bot.database.base import get_db

logger = logging.getLogger(__name__)


# ===================== KONSTANTALAR =====================

CURRENT_VERSION = 6  # ✅ Yangilandi: 5 -> 6


# ===================== VERSION JADVALI =====================

async def init_migrations_table() -> None:
    """Migrations jadvalini yaratish"""
    try:
        async with get_db() as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL UNIQUE,
                    description TEXT,
                    applied_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
        logger.info("✅ Migrations table initialized")
    except Exception as e:
        logger.error(f"❌ Migration table init error: {e}")


async def get_current_db_version() -> int:
    """Hozirgi database versiyasini olish"""
    try:
        async with get_db() as db:
            cursor = await db.execute("SELECT MAX(version) as version FROM migrations")
            result = await cursor.fetchone()
            return result['version'] if result and result['version'] else 0
    except Exception as e:
        logger.error(f"❌ get_current_db_version error: {e}")
        return 0


async def mark_migration_applied(version: int, description: str) -> bool:
    """Migration qo'llanganini belgilash"""
    try:
        async with get_db() as db:
            await db.execute("""
                INSERT INTO migrations (version, description)
                VALUES (?, ?)
            """, (version, description))
            await db.commit()
        logger.info(f"✅ Migration v{version} applied: {description}")
        return True
    except Exception as e:
        logger.error(f"❌ mark_migration_applied error: {e}")
        return False


# ===================== MIGRATION FUNKSIYALARI =====================

async def migration_v1_add_vip_status() -> bool:
    """Migration v1: users jadvaliga vip_status ustuni qo'shish"""
    try:
        async with get_db() as db:
            cursor = await db.execute("PRAGMA table_info(users)")
            columns = [row['name'] for row in await cursor.fetchall()]
            
            if 'vip_status' not in columns:
                await db.execute("ALTER TABLE users ADD COLUMN vip_status INTEGER DEFAULT 0")
                await db.commit()
                logger.info("✅ users jadvaliga 'vip_status' ustuni qo'shildi")
            else:
                logger.info("ℹ️ 'vip_status' ustuni allaqachon mavjud")
        return True
    except Exception as e:
        logger.error(f"❌ migration_v1 error: {e}")
        return False


async def migration_v2_add_channel_description() -> bool:
    """Migration v2: channels jadvaliga description ustuni qo'shish"""
    try:
        async with get_db() as db:
            cursor = await db.execute("PRAGMA table_info(channels)")
            columns = [row['name'] for row in await cursor.fetchall()]
            
            if 'description' not in columns:
                await db.execute("ALTER TABLE channels ADD COLUMN description TEXT")
                await db.commit()
                logger.info("✅ channels jadvaliga 'description' ustuni qo'shildi")
            else:
                logger.info("ℹ️ 'description' ustuni allaqachon mavjud")
        return True
    except Exception as e:
        logger.error(f"❌ migration_v2 error: {e}")
        return False


async def migration_v3_add_premium_expiry() -> bool:
    """Migration v3: users jadvaliga premium_expiry ustuni qo'shish"""
    try:
        async with get_db() as db:
            cursor = await db.execute("PRAGMA table_info(users)")
            columns = [row['name'] for row in await cursor.fetchall()]
            
            if 'premium_expiry' not in columns:
                await db.execute("ALTER TABLE users ADD COLUMN premium_expiry TEXT")
                await db.commit()
                logger.info("✅ users jadvaliga 'premium_expiry' ustuni qo'shildi")
            else:
                logger.info("ℹ️ 'premium_expiry' ustuni allaqachon mavjud")
        return True
    except Exception as e:
        logger.error(f"❌ migration_v3 error: {e}")
        return False


async def migration_v4_add_last_phone_update() -> bool:
    """Migration v4: users jadvaliga last_phone_update ustuni qo'shish"""
    try:
        async with get_db() as db:
            cursor = await db.execute("PRAGMA table_info(users)")
            columns = [row['name'] for row in await cursor.fetchall()]
            
            if 'last_phone_update' not in columns:
                await db.execute("ALTER TABLE users ADD COLUMN last_phone_update TEXT")
                await db.commit()
                logger.info("✅ users jadvaliga 'last_phone_update' ustuni qo'shildi")
            else:
                logger.info("ℹ️ 'last_phone_update' ustuni allaqachon mavjud")
        return True
    except Exception as e:
        logger.error(f"❌ migration_v4 error: {e}")
        return False


async def migration_v5_add_milestone_notified() -> bool:
    """Migration v5: users jadvaliga milestone_notified ustuni qo'shish"""
    try:
        async with get_db() as db:
            cursor = await db.execute("PRAGMA table_info(users)")
            columns = [row['name'] for row in await cursor.fetchall()]
            
            if 'milestone_notified' not in columns:
                await db.execute("ALTER TABLE users ADD COLUMN milestone_notified TEXT")
                await db.commit()
                logger.info("✅ users jadvaliga 'milestone_notified' ustuni qo'shildi")
            else:
                logger.info("ℹ️ 'milestone_notified' ustuni allaqachon mavjud")
        return True
    except Exception as e:
        logger.error(f"❌ migration_v5 error: {e}")
        return False


async def migration_v6_add_first_purchase_bonus_given() -> bool:
    """Migration v6: users jadvaliga first_purchase_bonus_given ustuni qo'shish"""
    try:
        async with get_db() as db:
            cursor = await db.execute("PRAGMA table_info(users)")
            columns = [row['name'] for row in await cursor.fetchall()]
            
            if 'first_purchase_bonus_given' not in columns:
                await db.execute("ALTER TABLE users ADD COLUMN first_purchase_bonus_given INTEGER DEFAULT 0")
                await db.commit()
                logger.info("✅ users jadvaliga 'first_purchase_bonus_given' ustuni qo'shildi")
            else:
                logger.info("ℹ️ 'first_purchase_bonus_given' ustuni allaqachon mavjud")
        return True
    except Exception as e:
        logger.error(f"❌ migration_v6 error: {e}")
        return False


# ===================== BARCHA MIGRATIONLAR =====================

MIGRATIONS: Dict[int, Dict[str, any]] = {
    1: {
        'function': migration_v1_add_vip_status,
        'description': 'Users jadvaliga vip_status qo\'shish'
    },
    2: {
        'function': migration_v2_add_channel_description,
        'description': 'Channels jadvaliga description qo\'shish'
    },
    3: {
        'function': migration_v3_add_premium_expiry,
        'description': 'Users jadvaliga premium_expiry qo\'shish'
    },
    4: {
        'function': migration_v4_add_last_phone_update,
        'description': 'Users jadvaliga last_phone_update qo\'shish'
    },
    5: {
        'function': migration_v5_add_milestone_notified,
        'description': 'Users jadvaliga milestone_notified qo\'shish'
    },
    6: {
        'function': migration_v6_add_first_purchase_bonus_given,
        'description': 'Users jadvaliga first_purchase_bonus_given qo\'shish'
    },
}


# ===================== MIGRATIONLARNI QO'LLASH =====================

async def run_migrations() -> Tuple[int, List[str]]:
    """
    Barcha qo'llanmagan migrationlarni ishga tushirish
    
    Returns:
        Tuple[int, List[str]]: (applied_count, errors)
    """
    errors = []
    applied_count = 0
    
    try:
        # 1. Migrations jadvalini yaratish
        await init_migrations_table()
        
        # 2. Hozirgi versiyani olish
        current_version = await get_current_db_version()
        logger.info(f"📊 Hozirgi database versiyasi: v{current_version}")
        
        # 3. Yangi migrationlarni qo'llash
        for version in sorted(MIGRATIONS.keys()):
            if version > current_version:
                migration = MIGRATIONS[version]
                logger.info(f"🔄 Migration v{version} qo'llanmoqda: {migration['description']}")
                
                try:
                    # Migration funksiyasini ishga tushirish
                    success = await migration['function']()
                    
                    if success:
                        # Migration qo'llanganini belgilash
                        await mark_migration_applied(version, migration['description'])
                        applied_count += 1
                        logger.info(f"✅ Migration v{version} muvaffaqiyatli qo'llandi")
                    else:
                        error_msg = f"Migration v{version} failed: {migration['description']}"
                        errors.append(error_msg)
                        logger.error(f"❌ {error_msg}")
                        
                except Exception as e:
                    error_msg = f"Migration v{version} error: {e}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
        
        if applied_count > 0:
            logger.info(f"✅ {applied_count} ta migration muvaffaqiyatli qo'llandi")
        else:
            logger.info("ℹ️ Yangi migrationlar yo'q")
            
        return applied_count, errors
        
    except Exception as e:
        logger.error(f"❌ run_migrations error: {e}")
        return applied_count, errors + [str(e)]


# ===================== UTILITY FUNKSIYALAR =====================

async def check_column_exists(table: str, column: str) -> bool:
    """
    Jadvalda ustun borligini tekshirish
    
    Args:
        table: Jadval nomi
        column: Ustun nomi
    
    Returns:
        bool: True agar ustun bo'lsa
    """
    try:
        async with get_db() as db:
            cursor = await db.execute(f"PRAGMA table_info({table})")
            columns = [row['name'] for row in await cursor.fetchall()]
            return column in columns
    except Exception as e:
        logger.error(f"❌ check_column_exists error: {e}")
        return False


async def add_column_if_not_exists(
    table: str, 
    column: str, 
    column_type: str, 
    default: any = None
) -> bool:
    """
    Agar ustun bo'lmasa, qo'shish
    
    Args:
        table: Jadval nomi
        column: Ustun nomi
        column_type: Ustun turi (TEXT, INTEGER, REAL, etc.)
        default: Default qiymat
    
    Returns:
        bool: Muvaffaqiyat
    """
    try:
        exists = await check_column_exists(table, column)
        
        if exists:
            logger.info(f"ℹ️ {table}.{column} allaqachon mavjud")
            return True
        
        default_clause = f" DEFAULT {default}" if default is not None else ""
        query = f"ALTER TABLE {table} ADD COLUMN {column} {column_type}{default_clause}"
        
        async with get_db() as db:
            await db.execute(query)
            await db.commit()
        
        logger.info(f"✅ {table}.{column} qo'shildi")
        return True
        
    except Exception as e:
        logger.error(f"❌ add_column_if_not_exists error: {e}")
        return False


async def get_migration_status() -> Dict[str, Any]:
    """
    Migration statusini olish
    
    Returns:
        dict: {
            'current_version': int,
            'total_migrations': int,
            'pending_migrations': list,
            'applied_migrations': list,
            'is_up_to_date': bool
        }
    """
    try:
        current = await get_current_db_version()
        total = len(MIGRATIONS)
        
        pending = []
        applied = []
        
        for version, migration in MIGRATIONS.items():
            if version > current:
                pending.append({
                    'version': version,
                    'description': migration['description']
                })
            else:
                applied.append({
                    'version': version,
                    'description': migration['description']
                })
        
        return {
            'current_version': current,
            'total_migrations': total,
            'pending_migrations': pending,
            'applied_migrations': applied,
            'is_up_to_date': current >= total
        }
    except Exception as e:
        logger.error(f"❌ get_migration_status error: {e}")
        return {
            'current_version': 0,
            'total_migrations': 0,
            'pending_migrations': [],
            'applied_migrations': [],
            'is_up_to_date': False
        }


async def get_migration_history(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Migration tarixini olish
    
    Args:
        limit: Nechta migration
    
    Returns:
        list: Migrationlar ro'yxati (eng yangidan eskiyga)
    """
    try:
        async with get_db() as db:
            cursor = await db.execute("""
                SELECT * FROM migrations 
                ORDER BY applied_at DESC 
                LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ get_migration_history error: {e}")
        return []


# ===================== ROLLBACK =====================

async def rollback_last_migration() -> Tuple[bool, str]:
    """
    Oxirgi migration ni bekor qilish
    
    DIQQAT: SQLite da ustunni o'chirish murakkab!
    Faqat migrations jadvalidan versionni o'chiradi.
    Ustunlar O'CHIRILMAYDI!
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        current = await get_current_db_version()
        
        if current == 0:
            return False, "Hech qanday migration topilmadi"
        
        async with get_db() as db:
            await db.execute("DELETE FROM migrations WHERE version = ?", (current,))
            await db.commit()
        
        logger.warning(f"⚠️ Migration v{current} rollback qilindi (faqat belgi o'chirildi)")
        return True, f"Migration v{current} rollback qilindi (faqat belgi o'chirildi, ustunlar saqlanib qoldi)"
        
    except Exception as e:
        logger.error(f"❌ rollback_last_migration error: {e}")
        return False, str(e)


async def rollback_to_version(target_version: int) -> Tuple[bool, str, List[int]]:
    """
    Ma'lum versiyagacha rollback qilish
    
    Args:
        target_version: Qaysi versiyagacha (bu versiyadan kichiklar qoladi)
    
    Returns:
        Tuple[bool, str, List[int]]: (success, message, rolled_back_versions)
    """
    try:
        current = await get_current_db_version()
        
        if target_version >= current:
            return False, f"Target version {target_version} >= current version {current}", []
        
        rolled_back = []
        
        for version in range(current, target_version, -1):
            if version in MIGRATIONS:
                async with get_db() as db:
                    await db.execute("DELETE FROM migrations WHERE version = ?", (version,))
                    await db.commit()
                rolled_back.append(version)
                logger.warning(f"⚠️ Migration v{version} rollback qilindi")
        
        return True, f"{len(rolled_back)} ta migration rollback qilindi", rolled_back
        
    except Exception as e:
        logger.error(f"❌ rollback_to_version error: {e}")
        return False, str(e), []


# ===================== DIAGNOSTIKA =====================

async def diagnose_migrations() -> Dict[str, Any]:
    """
    Migrationlarni diagnostika qilish
    
    Returns:
        dict: Diagnostika natijalari
    """
    try:
        result = {
            'status': await get_migration_status(),
            'history': await get_migration_history(10),
            'table_exists': False,
            'table_columns': []
        }
        
        # Jadval mavjudligini tekshirish
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'"
            )
            table_exists = await cursor.fetchone()
            result['table_exists'] = bool(table_exists)
            
            if result['table_exists']:
                cursor = await db.execute("PRAGMA table_info(migrations)")
                result['table_columns'] = [row['name'] for row in await cursor.fetchall()]
        
        return result
        
    except Exception as e:
        logger.error(f"❌ diagnose_migrations error: {e}")
        return {
            'status': {},
            'history': [],
            'table_exists': False,
            'table_columns': [],
            'error': str(e)
        }


# ===================== FORCE FIX =====================

async def force_set_version(version: int) -> Tuple[bool, str]:
    """
    Versiyani majburan o'rnatish (DIQQAT bilan ishlating!)
    
    Args:
        version: Yangi versiya raqami
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        current = await get_current_db_version()
        
        if version < current:
            # Pastki versiyaga o'tish
            async with get_db() as db:
                await db.execute("DELETE FROM migrations WHERE version > ?", (version,))
                await db.commit()
            logger.warning(f"⚠️ Force set version to {version} (was {current})")
            return True, f"Versiya {version} ga o'rnatildi (pastki versiya)"
            
        elif version > current:
            # Yuqori versiyaga o'tish - migrationlarni qo'llash kerak
            return False, f"Yuqori versiyaga o'tish uchun run_migrations() ni ishlating"
        
        else:
            return True, f"Versiya allaqachon {version}"
            
    except Exception as e:
        logger.error(f"❌ force_set_version error: {e}")
        return False, str(e)


# ===================== EXPORT =====================

__all__ = [
    # Main
    'run_migrations',
    'get_current_db_version',
    'get_migration_status',
    
    # Utility
    'check_column_exists',
    'add_column_if_not_exists',
    'get_migration_history',
    
    # Rollback
    'rollback_last_migration',
    'rollback_to_version',
    
    # Diagnostic
    'diagnose_migrations',
    'force_set_version',
    
    # Constants
    'CURRENT_VERSION',
    'MIGRATIONS'
]