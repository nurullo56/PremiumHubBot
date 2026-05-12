# bot/database/uow/uow.py
"""Unit of Work pattern for managing database transactions."""
import logging
from typing import Optional

import aiosqlite

from bot.database.base import get_db
from bot.database.repositories.user_repo import UserRepository
from bot.database.repositories.balance_repo import BalanceRepository
from bot.database.repositories.referral_repo import ReferralRepository
from bot.database.repositories.channel_repo import ChannelRepository
from bot.database.repositories.transaction_repo import TransactionRepository
from bot.database.repositories.promocode_repo import PromocodeRepository
from bot.database.repositories.premium_repo import PremiumRepository
from bot.database.repositories.join_request_repo import JoinRequestRepository
from bot.database.repositories.fraud_repo import FraudRepository
from bot.database.repositories.statistics_repo import StatisticsRepository

logger = logging.getLogger(__name__)


class UnitOfWork:
    """
    Unit of Work pattern for managing database transactions.
    
    Usage:
        async with UnitOfWork() as uow:
            await uow.users.create(...)
            await uow.balance.add_balance(...)
            await uow.commit()
    """
    
    def __init__(self):
        self._db: Optional[aiosqlite.Connection] = None
        self._db_context = None
        
        # Create repository instances
        self.users = UserRepository()
        self.balance = BalanceRepository()
        self.referrals = ReferralRepository()
        self.channels = ChannelRepository()
        self.transactions = TransactionRepository()
        self.promocodes = PromocodeRepository()
        self.premium = PremiumRepository()
        self.join_requests = JoinRequestRepository()
        self.fraud = FraudRepository()
        self.statistics = StatisticsRepository()
        
        # List of all repositories for easy iteration
        self._repositories = [
            self.users, self.balance, self.referrals, self.channels,
            self.transactions, self.promocodes, self.premium,
            self.join_requests, self.fraud, self.statistics
        ]
    
    async def __aenter__(self):
        """Enter context manager - open database connection"""
        self._db_context = get_db()
        self._db = await self._db_context.__aenter__()
        
        # ✅ Set database connection to ALL repositories
        for repo in self._repositories:
            if hasattr(repo, 'set_db'):
                repo.set_db(self._db)
        
        logger.debug("🔓 UnitOfWork started")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager - handle transaction and close connection"""
        if exc_type is not None:
            # Error occurred - rollback transaction
            logger.error(f"❌ Transaction failed: {exc_val}")
            await self.rollback()
        
        # Close database connection
        await self._db_context.__aexit__(exc_type, exc_val, exc_tb)
        self._db = None
        
        # Clear database connections from repositories
        for repo in self._repositories:
            if hasattr(repo, 'set_db'):
                repo.set_db(None)
        
        logger.debug("🔒 UnitOfWork finished")
    
    async def commit(self):
        """Commit the current transaction"""
        if self._db:
            await self._db.commit()
            logger.info("✅ Transaction committed")
    
    async def rollback(self):
        """Rollback the current transaction"""
        if self._db:
            await self._db.rollback()
            logger.warning("⚠️ Transaction rolled back")