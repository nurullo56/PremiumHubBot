"""Channel service - business logic."""

import logging
from typing import List, Dict, Any, Optional

from bot.database.repositories.channel_repo import channel_repo
from bot.utils.common.timezone import now_str

logger = logging.getLogger(__name__)


class ChannelService:
    
    async def add_channel(
        self,
        channel_id: str,
        channel_name: str,
        channel_url: str,
        added_by: Optional[int] = None,
        description: Optional[str] = None
    ) -> bool:
        timestamp = now_str()
        return await channel_repo.create(
            channel_id=channel_id,
            channel_name=channel_name,
            channel_url=channel_url,
            added_by=added_by,
            description=description,
            created_at=timestamp
        )
    
    async def get_active_channels(self) -> List[Dict[str, Any]]:
        return await channel_repo.get_all_active()
    
    async def get_all_channels(self) -> List[Dict[str, Any]]:
        return await channel_repo.get_all()
    
    async def activate_channel(self, channel_id: str) -> bool:
        return await channel_repo.activate(channel_id)
    
    async def deactivate_channel(self, channel_id: str) -> bool:
        return await channel_repo.deactivate(channel_id)
    
    async def remove_channel(self, channel_id: str) -> bool:
        return await channel_repo.delete(channel_id)
    
    async def get_channel_count(self) -> int:
        return await channel_repo.get_count()


channel_service = ChannelService()
