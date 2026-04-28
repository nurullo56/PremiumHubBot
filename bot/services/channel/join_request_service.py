"""Join request service - business logic."""

import logging
from typing import Optional, Dict, Any

from bot.database.repositories.join_request_repo import join_request_repo
from bot.utils.common.timezone import now_str

logger = logging.getLogger(__name__)


class JoinRequestService:
    
    async def create_managed_chat(
        self,
        chat_id: str,
        fullname: str,
        chat_type: str,
        invite_link: Optional[str] = None,
        added_by: Optional[int] = None,
        description: Optional[str] = None
    ) -> bool:
        timestamp = now_str()
        
        return await join_request_repo.create_chat(
            chat_id=chat_id,
            fullname=fullname,
            chat_type=chat_type,
            invite_link=invite_link,
            added_date=timestamp,
            added_by=added_by,
            description=description
        )
    
    async def get_managed_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        return await join_request_repo.get_chat(chat_id)
    
    async def get_all_active_chats(self):
        return await join_request_repo.get_all_active_chats()
    
    async def create_join_request(self, user_id: int, chat_id: str) -> bool:
        timestamp = now_str()
        
        success = await join_request_repo.create_request(user_id, chat_id, timestamp)
        
        if success:
            logger.info(f"✅ Join request created: user={user_id}, chat={chat_id}")
        
        return success
    
    async def get_join_request(self, user_id: int, chat_id: str) -> Optional[Dict[str, Any]]:
        return await join_request_repo.get_request(user_id, chat_id)
    
    async def approve_request(self, user_id: int, chat_id: str, processed_by: int) -> bool:
        timestamp = now_str()
        
        success = await join_request_repo.approve_request(user_id, chat_id, timestamp, processed_by)
        
        if success:
            logger.info(f"✅ Join request approved: user={user_id}, chat={chat_id}")
        
        return success
    
    async def reject_request(self, user_id: int, chat_id: str, processed_by: int) -> bool:
        timestamp = now_str()
        
        success = await join_request_repo.reject_request(user_id, chat_id, timestamp, processed_by)
        
        if success:
            logger.info(f"⚠️ Join request rejected: user={user_id}, chat={chat_id}")
        
        return success


join_request_service = JoinRequestService()
