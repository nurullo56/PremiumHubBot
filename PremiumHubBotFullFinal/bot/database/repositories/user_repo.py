"""User repository - database access only."""

import logging
from typing import Dict, Any, Optional, Tuple, List

from bot.database.base import get_db

logger = logging.getLogger(__name__)


class UserRepository:
    
    @staticmethod
    async def create(
        user_id: int,
        username: Optional[str],
        fullname: str,
        phone: Optional[str] = None,
        referred_by: Optional[int] = None,
        registration_date: str = None
    ) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    INSERT INTO users (
                        user_id, username, fullname, phone, referred_by,
                        registration_date, last_activity, balance, bonus_status,
                        referral_bonus_given, last_phone_update
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0.0, 0, 0, ?)
                """, (user_id, username, fullname, phone, referred_by, 
                      registration_date, registration_date, 
                      registration_date if phone else None))
                await db.commit()
                logger.info(f"✅ User created: {user_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create user {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get user {user_id}: {e}")
            return None
    
    @staticmethod
    async def get_by_username(username: str) -> Optional[Dict[str, Any]]:
        try:
            username = username.lstrip('@')
            async with get_db() as db:
                cursor = await db.execute("SELECT * FROM users WHERE username = ?", (username,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get user by username: {e}")
            return None
    
    @staticmethod
    async def get_by_phone(phone: str) -> Optional[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT * FROM users WHERE phone = ?", (phone,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get user by phone: {e}")
            return None
    
    @staticmethod
    async def exists(user_id: int) -> bool:
        user = await UserRepository.get_by_id(user_id)
        return user is not None
    
    @staticmethod
    async def phone_exists(phone: str) -> Tuple[bool, Optional[int]]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT user_id, is_blocked FROM users WHERE phone = ?", (phone,)
                )
                result = await cursor.fetchone()
                return (True, result['user_id']) if result else (False, None)
        except Exception as e:
            logger.error(f"❌ Failed to check phone: {e}")
            return False, None
    
    @staticmethod
    async def update(user_id: int, data: Dict[str, Any]) -> bool:
        """Universal update method for any user fields"""
        try:
            if not data:
                return False
            
            # Build dynamic UPDATE query
            fields = ', '.join([f"{key} = ?" for key in data.keys()])
            values = list(data.values())
            values.append(user_id)
            
            async with get_db() as db:
                await db.execute(
                    f"UPDATE users SET {fields} WHERE user_id = ?",
                    tuple(values)
                )
                await db.commit()
                logger.info(f"✅ User {user_id} updated: {list(data.keys())}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update user {user_id}: {e}")
            return False
    
    @staticmethod
    async def update_phone(user_id: int, phone: str, timestamp: str) -> bool:
        try:
            async with get_db() as db:
                await db.execute(
                    "UPDATE users SET phone = ?, last_phone_update = ? WHERE user_id = ?",
                    (phone, timestamp, user_id)
                )
                await db.commit()
                logger.info(f"✅ Phone updated for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update phone for {user_id}: {e}")
            return False

    @staticmethod
    async def update_phone_atomic(
        user_id: int, phone: str, timestamp: str
    ) -> Tuple[bool, Optional[int]]:
        """
        Atomically assign phone to user only when no other user holds it.

        Returns:
            (True, None)          — success
            (False, other_id)     — another user already has this phone
            (False, None)         — unexpected DB error
        """
        try:
            async with get_db() as db:
                cursor = await db.execute("""
                    UPDATE users
                    SET phone = ?, last_phone_update = ?
                    WHERE user_id = ?
                      AND NOT EXISTS (
                          SELECT 1 FROM users
                          WHERE phone = ? AND user_id != ?
                      )
                """, (phone, timestamp, user_id, phone, user_id))
                await db.commit()

                if cursor.rowcount > 0:
                    logger.info(f"✅ Phone atomically set for user {user_id}")
                    return True, None

                # Find the conflicting owner
                cursor = await db.execute(
                    "SELECT user_id FROM users WHERE phone = ? AND user_id != ?",
                    (phone, user_id)
                )
                row = await cursor.fetchone()
                return False, row['user_id'] if row else None
        except Exception as e:
            logger.error(f"❌ Failed to atomically update phone for {user_id}: {e}")
            return False, None
    
    @staticmethod
    async def update_gender(user_id: int, gender: str) -> bool:
        try:
            async with get_db() as db:
                await db.execute("UPDATE users SET gender = ? WHERE user_id = ?", (gender, user_id))
                await db.commit()
                logger.info(f"✅ Gender updated for user {user_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update gender for {user_id}: {e}")
            return False
    
    @staticmethod
    async def update_subscription(user_id: int, is_subscribed: bool) -> bool:
        try:
            async with get_db() as db:
                await db.execute(
                    "UPDATE users SET is_subscribed = ? WHERE user_id = ?",
                    (1 if is_subscribed else 0, user_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update subscription for {user_id}: {e}")
            return False
    
    @staticmethod
    async def mark_captcha_passed(user_id: int) -> bool:
        try:
            async with get_db() as db:
                await db.execute("UPDATE users SET captcha_passed = 1 WHERE user_id = ?", (user_id,))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to mark captcha passed for {user_id}: {e}")
            return False
    
    @staticmethod
    async def update_last_activity(user_id: int, timestamp: str) -> bool:
        try:
            async with get_db() as db:
                await db.execute(
                    "UPDATE users SET last_activity = ? WHERE user_id = ?",
                    (timestamp, user_id)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update last activity for {user_id}: {e}")
            return False
    
    @staticmethod
    async def block_user(user_id: int) -> bool:
        try:
            async with get_db() as db:
                await db.execute(
                    "UPDATE users SET is_blocked = 1, username = NULL, phone = NULL WHERE user_id = ?",
                    (user_id,)
                )
                await db.commit()
                logger.info(f"✅ User blocked: {user_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to block user {user_id}: {e}")
            return False
    
    @staticmethod
    async def unblock_user(user_id: int) -> bool:
        try:
            async with get_db() as db:
                await db.execute("UPDATE users SET is_blocked = 0 WHERE user_id = ?", (user_id,))
                await db.commit()
                logger.info(f"✅ User unblocked: {user_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to unblock user {user_id}: {e}")
            return False
    
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        try:
            async with get_db() as db:
                await db.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
                await db.execute("DELETE FROM balance_history WHERE user_id = ?", (user_id,))
                await db.execute("DELETE FROM join_requests WHERE user_id = ?", (user_id,))
                await db.execute("DELETE FROM fraud_logs WHERE user_id = ?", (user_id,))
                await db.execute("DELETE FROM promocodes WHERE user_id = ?", (user_id,))
                await db.execute("DELETE FROM rate_limits WHERE user_id = ?", (user_id,))
                await db.execute("DELETE FROM ip_tracking WHERE user_id = ?", (user_id,))
                await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                await db.commit()
                logger.info(f"✅ User deleted permanently: {user_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to delete user {user_id}: {e}")
            return False
    
    @staticmethod
    async def get_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT * FROM users ORDER BY registration_date DESC LIMIT ? OFFSET ?",
                    (limit, offset)
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get all users: {e}")
            return []
    
    @staticmethod
    async def get_total_count() -> int:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT COUNT(*) as count FROM users")
                result = await cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Failed to get total users count: {e}")
            return 0
    
    @staticmethod
    async def get_subscribed_count() -> int:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE is_subscribed = 1")
                result = await cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Failed to get subscribed count: {e}")
            return 0
    
    @staticmethod
    async def get_with_phone_count() -> int:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE phone IS NOT NULL")
                result = await cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Failed to get users with phone count: {e}")
            return 0
    
    @staticmethod
    async def get_gender_counts() -> Tuple[int, int]:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE gender = 'male'")
                male_count = (await cursor.fetchone())['count']
                
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE gender = 'female'")
                female_count = (await cursor.fetchone())['count']
                
                return male_count, female_count
        except Exception as e:
            logger.error(f"❌ Failed to get gender counts: {e}")
            return 0, 0
    
    @staticmethod
    async def get_blocked_count() -> int:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT COUNT(*) as count FROM users WHERE is_blocked = 1")
                result = await cursor.fetchone()
                return result['count'] if result else 0
        except Exception as e:
            logger.error(f"❌ Failed to get blocked count: {e}")
            return 0


user_repo = UserRepository()