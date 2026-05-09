"""Join request repository - database access only."""

import logging
from typing import List, Dict, Any, Optional

from bot.database.base import get_db

logger = logging.getLogger(__name__)


class JoinRequestRepository:
    
    @staticmethod
    async def create_chat(
        chat_id: str,
        fullname: str,
        chat_type: str,
        invite_link: Optional[str],
        added_date: str,
        added_by: Optional[int] = None,
        description: Optional[str] = None
    ) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    INSERT INTO managed_chats (
                        chat_id, fullname, chat_type, invite_link, added_date, added_by, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (chat_id, fullname, chat_type, invite_link, added_date, added_by, description))
                await db.commit()
                logger.info(f"✅ Managed chat created: {fullname}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create managed chat {chat_id}: {e}")
            return False
    
    @staticmethod
    async def get_chat(chat_id: str) -> Optional[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute("SELECT * FROM managed_chats WHERE chat_id = ?", (chat_id,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get managed chat {chat_id}: {e}")
            return None
    
    @staticmethod
    async def get_chat_by_title(title: str) -> Optional[Dict[str, Any]]:
        """Find managed chat by fullname (for ID mismatch correction)."""
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT * FROM managed_chats WHERE fullname = ? AND is_active = 1",
                    (title,)
                )
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get managed chat by title '{title}': {e}")
            return None

    @staticmethod
    async def fix_chat_id(old_id: str, new_id: str) -> bool:
        """Correct a wrong chat_id in managed_chats and join_requests."""
        try:
            async with get_db() as db:
                await db.execute(
                    "UPDATE managed_chats SET chat_id = ? WHERE chat_id = ?",
                    (new_id, old_id)
                )
                await db.execute(
                    "UPDATE join_requests SET chat_id = ? WHERE chat_id = ?",
                    (new_id, old_id)
                )
                await db.commit()
                logger.info(f"✅ Chat ID corrected: {old_id} → {new_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to fix chat_id {old_id} → {new_id}: {e}")
            return False

    @staticmethod
    async def get_all_active_chats() -> List[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT * FROM managed_chats WHERE is_active = 1 ORDER BY added_date DESC"
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"❌ Failed to get active managed chats: {e}")
            return []
    
    @staticmethod
    async def create_request(user_id: int, chat_id: str, request_date: str) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    INSERT OR REPLACE INTO join_requests (user_id, chat_id, has_requested, request_date)
                    VALUES (?, ?, 1, ?)
                """, (user_id, chat_id, request_date))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create join request for {user_id}: {e}")
            return False
    
    @staticmethod
    async def clear_request(user_id: int, chat_id: str) -> bool:
        """User kanaldan chiqqanda has_requested=0 qilib belgilash."""
        try:
            async with get_db() as db:
                await db.execute(
                    "UPDATE join_requests SET has_requested = 0 WHERE user_id = ? AND chat_id = ?",
                    (user_id, str(chat_id))
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to clear join request for {user_id}: {e}")
            return False

    @staticmethod
    async def get_request(user_id: int, chat_id: str) -> Optional[Dict[str, Any]]:
        try:
            async with get_db() as db:
                cursor = await db.execute(
                    "SELECT * FROM join_requests WHERE user_id = ? AND chat_id = ?",
                    (user_id, chat_id)
                )
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"❌ Failed to get join request for {user_id}: {e}")
            return None
    
    @staticmethod
    async def approve_request(user_id: int, chat_id: str, approved_date: str, processed_by: int) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    UPDATE join_requests 
                    SET status = 'approved', approved_date = ?, processed_by = ?, processed_date = ?
                    WHERE user_id = ? AND chat_id = ?
                """, (approved_date, processed_by, approved_date, user_id, chat_id))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to approve join request for {user_id}: {e}")
            return False
    
    @staticmethod
    async def reject_request(user_id: int, chat_id: str, rejected_date: str, processed_by: int) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    UPDATE join_requests 
                    SET status = 'rejected', rejected_date = ?, processed_by = ?, processed_date = ?
                    WHERE user_id = ? AND chat_id = ?
                """, (rejected_date, processed_by, rejected_date, user_id, chat_id))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to reject join request for {user_id}: {e}")
            return False
    
    @staticmethod
    async def update_request(
        user_id: int,
        chat_id: str,
        has_requested: bool,
        status: str = "pending"
    ) -> tuple[bool, str]:
        """
        Update or create join request.
        
        Args:
            user_id: User ID
            chat_id: Chat ID
            has_requested: Has user requested
            status: Request status (pending, approved, rejected)
        
        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            from datetime import datetime
            request_date = datetime.now().isoformat()
            
            async with get_db() as db:
                await db.execute("""
                    INSERT OR REPLACE INTO join_requests 
                    (user_id, chat_id, has_requested, status, request_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, chat_id, has_requested, status, request_date))
                await db.commit()
                
                logger.info(f"✅ Join request updated: {user_id} -> {chat_id} (status={status})")
                return True, "Success"
                
        except Exception as e:
            logger.error(f"❌ Failed to update join request: {e}")
            return False, str(e)
    
    @staticmethod
    async def get_chat_by_id(chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get managed chat by ID (alias for get_chat).
        
        Args:
            chat_id: Chat ID
        
        Returns:
            Chat dict or None
        """
        return await JoinRequestRepository.get_chat(chat_id)


join_request_repo = JoinRequestRepository()
