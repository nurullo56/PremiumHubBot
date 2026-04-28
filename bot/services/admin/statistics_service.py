# bot/services/admin/statistics_service.py
"""Statistics service for admin panel."""

import logging
from typing import Dict, Any, List

from bot.database.repositories.statistics_repo import statistics_repo

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for gathering bot statistics."""
    
    async def get_overview(self) -> Dict[str, Any]:
        """Get overview statistics."""
        return await statistics_repo.get_overview()
    
    async def get_growth_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get growth statistics for last N days."""
        return await statistics_repo.get_growth_stats(days)
    
    async def get_daily_users_chart(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily new users for last N days."""
        return await statistics_repo.get_daily_users_chart(days)
    
    async def get_daily_active_chart(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily active users for last N days."""
        return await statistics_repo.get_daily_active_chart(days)
    
    async def get_users_by_weekday(self) -> List[Dict[str, Any]]:
        """Get user registration by weekday."""
        return await statistics_repo.get_users_by_weekday()
    
    async def get_retention_stats(self) -> Dict[str, Any]:
        """Get retention statistics (1, 7, 30 days)."""
        try:
            day1 = await statistics_repo.get_retention_rate(1)
            day7 = await statistics_repo.get_retention_rate(7)
            day30 = await statistics_repo.get_retention_rate(30)
            
            return {
                'day1': day1,
                'day7': day7,
                'day30': day30
            }
        except Exception as e:
            logger.error(f"Failed to get retention stats: {e}")
            return {}
    
    async def get_conversion_funnel(self) -> Dict[str, Any]:
        """Get conversion funnel statistics."""
        return await statistics_repo.get_conversion_funnel()
    
    async def get_full_statistics(self) -> Dict[str, Any]:
        """Get full statistics with all details."""
        return await statistics_repo.get_full_statistics()


# Singleton instance
statistics_service = StatisticsService()