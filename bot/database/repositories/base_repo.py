"""Base repository with database connection management for UnitOfWork pattern."""
import logging
from typing import Optional, Dict, Any, List

import aiosqlite

logger = logging.getLogger(__name__)


class BaseRepository:
    """
    Base class for all repositories.
    Provides database connection management for UnitOfWork pattern.
    
    Usage:
        class UserRepository(BaseRepository):
            async def get_by_id(self, user_id: int):
                return await self.fetch_one(
                    "SELECT * FROM users WHERE user_id = ?", 
                    (user_id,)
                )
    """
    
    def __init__(self):
        self._db: Optional[aiosqlite.Connection] = None
    
    def set_db(self, db: aiosqlite.Connection):
        """Set database connection (called by UnitOfWork)"""
        self._db = db
    
    def _check_connection(self):
        """Check if database connection is set"""
        if not self._db:
            raise RuntimeError(
                "Database connection not set. "
                "Use repository inside UnitOfWork context manager."
            )
    
    async def _execute(self, sql: str, params: tuple = ()):
        """Execute SQL query and return cursor"""
        self._check_connection()
        return await self._db.execute(sql, params)
    
    async def _commit(self):
        """Commit current transaction"""
        self._check_connection()
        await self._db.commit()
    
    async def _rollback(self):
        """Rollback current transaction"""
        self._check_connection()
        await self._db.rollback()
    
    async def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch single row as dictionary"""
        async with self._execute(sql, params) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def fetch_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows as list of dictionaries"""
        async with self._execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def execute_and_commit(self, sql: str, params: tuple = ()) -> int:
        """Execute SQL, commit, return rowcount"""
        async with self._execute(sql, params) as cursor:
            await self._commit()
            return cursor.rowcount