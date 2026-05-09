# bot/database/repositories/statistics_repo.py
"""Statistics repository - aggregation queries."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from bot.database.base import get_db

logger = logging.getLogger(__name__)


class StatisticsRepository:
    
    @staticmethod
    async def get_overview() -> Dict[str, Any]:
        """Asosiy statistika"""
        try:
            async with get_db() as db:
                stats = {}
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM users")
                stats['total_users'] = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE is_subscribed = 1")
                stats['subscribed_users'] = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE phone IS NOT NULL")
                stats['users_with_phone'] = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE balance > 0")
                stats['users_with_balance'] = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT SUM(balance) as total FROM users")
                result = await cursor.fetchone()
                stats['total_balance'] = result['total'] if result and result['total'] else 0
                
                cursor = await db.execute("SELECT SUM(referral_count) as total FROM users")
                result = await cursor.fetchone()
                stats['total_referrals'] = result['total'] if result and result['total'] else 0
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM channels WHERE is_active = 1")
                stats['active_channels'] = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM promocodes WHERE is_used = 0")
                stats['unused_promocodes'] = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE premium_status = 'pending'")
                stats['pending_premium'] = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE premium_status IN ('active', 'approved')")
                stats['active_premium'] = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE gender = 'male'")
                stats['male_users'] = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE gender = 'female'")
                stats['female_users'] = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE is_blocked = 1")
                stats['blocked_users'] = (await cursor.fetchone())['count']
                
                return stats
        except Exception as e:
            logger.error(f"❌ Failed to get statistics overview: {e}")
            return {}
    
    @staticmethod
    async def get_growth_stats(days: int = 7) -> Dict[str, Any]:
        """O'sish statistikasi"""
        try:
            async with get_db() as db:
                stats = {}
                
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM users WHERE DATE(registration_date) >= DATE('now', ?)",
                    (f'-{days} days',)
                )
                stats[f'new_users_{days}d'] = (await cursor.fetchone())['count']
                
                cursor = await db.execute(
                    "SELECT COUNT(*) as count FROM transactions WHERE DATE(created_at) >= DATE('now', ?)",
                    (f'-{days} days',)
                )
                stats[f'transactions_{days}d'] = (await cursor.fetchone())['count']
                
                return stats
        except Exception as e:
            logger.error(f"❌ Failed to get growth stats: {e}")
            return {}
    
    @staticmethod
    async def get_daily_users_chart(days: int = 7) -> List[Dict[str, Any]]:
        """Kunlik userlar grafigi"""
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT DATE(registration_date) AS date, COUNT(*) AS count
                    FROM users
                    WHERE DATE(registration_date) >= DATE('now', ?)
                    GROUP BY DATE(registration_date)
                    ORDER BY date ASC
                """, (f'-{days} days',))
                rows = await cursor.fetchall()

            # Fill in any missing days with 0 so the chart always has `days` points
            date_map = {row['date']: row['count'] for row in rows}
            result = []
            for i in range(days - 1, -1, -1):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                result.append({'date': date, 'count': date_map.get(date, 0)})
            return result
        except Exception as e:
            logger.error(f"❌ Failed to get daily users chart: {e}")
            return []

    @staticmethod
    async def get_daily_active_chart(days: int = 7) -> List[Dict[str, Any]]:
        """Kunlik aktiv userlar grafigi"""
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT DATE(last_activity) AS date, COUNT(*) AS active_count
                    FROM users
                    WHERE DATE(last_activity) >= DATE('now', ?)
                      AND is_blocked = 0
                    GROUP BY DATE(last_activity)
                    ORDER BY date ASC
                """, (f'-{days} days',))
                rows = await cursor.fetchall()

            date_map = {row['date']: row['active_count'] for row in rows}
            result = []
            for i in range(days - 1, -1, -1):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                result.append({'date': date, 'active_count': date_map.get(date, 0)})
            return result
        except Exception as e:
            logger.error(f"❌ Failed to get daily active chart: {e}")
            return []
    
    @staticmethod
    async def get_users_by_weekday() -> List[Dict[str, Any]]:
        """Hafta kuni bo'yicha statistika"""
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    SELECT 
                        CAST(strftime('%w', registration_date) AS INTEGER) as weekday,
                        COUNT(*) as cnt
                    FROM users 
                    GROUP BY weekday
                    ORDER BY weekday ASC
                """)
                results = await cursor.fetchall()
                
                weekdays = ['Yakshanba', 'Dushanba', 'Seshanba', 'Chorshanba', 
                           'Payshanba', 'Juma', 'Shanba']
                
                return [
                    {
                        'weekday': weekdays[row['weekday']],
                        'weekday_num': row['weekday'],
                        'count': row['cnt']
                    }
                    for row in results
                ]
        except Exception as e:
            logger.error(f"❌ Failed to get weekday stats: {e}")
            return []
    
    @staticmethod
    async def get_retention_rate(days: int = 7) -> Dict[str, Any]:
        """Retention rate"""
        try:
            period_ago = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) as cnt FROM users WHERE registration_date < ?",
                    (period_ago,)
                )
                old_users = (await cursor.fetchone())['cnt']
                
                cursor = await db.execute("""
                    SELECT COUNT(*) as cnt FROM users 
                    WHERE registration_date < ? AND last_activity >= ?
                """, (period_ago, period_ago))
                returned_users = (await cursor.fetchone())['cnt']
                
                retention_rate = round((returned_users / old_users * 100), 2) if old_users > 0 else 0
                
                return {
                    'returned_users': returned_users,
                    'old_users': old_users,
                    'retention_rate': retention_rate
                }
        except Exception as e:
            logger.error(f"❌ Failed to get retention rate: {e}")
            return {'returned_users': 0, 'old_users': 0, 'retention_rate': 0}
    
    @staticmethod
    async def get_conversion_funnel() -> Dict[str, Any]:
        """Konversion voronka"""
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT COUNT(*) as cnt FROM users")
                total = (await cursor.fetchone())['cnt']
                
                cursor = await db.execute(
                    "SELECT COUNT(*) as cnt FROM users WHERE phone IS NOT NULL"
                )
                with_phone = (await cursor.fetchone())['cnt']
                
                cursor = await db.execute(
                    "SELECT COUNT(*) as cnt FROM users WHERE premium_status = 'approved'"
                )
                premium = (await cursor.fetchone())['cnt']
                
                cursor = await db.execute("""
                    SELECT COUNT(DISTINCT user_id) as cnt 
                    FROM transactions 
                    WHERE transaction_type IN ('spend', 'subtract')
                """)
                purchased = (await cursor.fetchone())['cnt']
                
                return {
                    'total_users': total,
                    'with_phone': with_phone,
                    'premium_users': premium,
                    'purchased_users': purchased,
                    'conversion_rates': {
                        'phone_to_premium': round((premium / with_phone * 100), 2) if with_phone > 0 else 0,
                        'premium_to_purchase': round((purchased / premium * 100), 2) if premium > 0 else 0,
                        'overall': round((purchased / total * 100), 2) if total > 0 else 0
                    }
                }
        except Exception as e:
            logger.error(f"❌ Failed to get conversion funnel: {e}")
            return {}
    
    @staticmethod
    async def get_full_statistics() -> Dict[str, Any]:
        """To'liq statistika"""
        try:
            overview = await StatisticsRepository.get_overview()
            growth = await StatisticsRepository.get_growth_stats(7)
            daily_users = await StatisticsRepository.get_daily_users_chart(7)
            daily_active = await StatisticsRepository.get_daily_active_chart(7)
            weekday = await StatisticsRepository.get_users_by_weekday()
            retention = {
                'day1': await StatisticsRepository.get_retention_rate(1),
                'day7': await StatisticsRepository.get_retention_rate(7),
                'day30': await StatisticsRepository.get_retention_rate(30),
            }
            funnel = await StatisticsRepository.get_conversion_funnel()
            
            return {
                'overview': overview,
                'growth': growth,
                'charts': {
                    'daily_users': daily_users,
                    'daily_active': daily_active,
                    'weekday': weekday,
                },
                'retention': retention,
                'conversion_funnel': funnel
            }
        except Exception as e:
            logger.error(f"❌ Failed to get full statistics: {e}")
            return {}


statistics_repo = StatisticsRepository()