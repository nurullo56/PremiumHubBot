"""Subscription service - business logic."""

import logging
from typing import List

from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from bot.database.repositories.user_repo import user_repo
from bot.services.channel.channel_service import channel_service

logger = logging.getLogger(__name__)


class SubscriptionService:
    
    async def check_user_subscriptions(self, bot: Bot, user_id: int) -> tuple[bool, List[str]]:
        """
        Check if user subscribed to all required channels.
        
        Returns:
            tuple[bool, List[str]]: (all_subscribed, unsubscribed_channel_ids)
        """
        channels = await channel_service.get_active_channels()
        
        if not channels:
            return True, []
        
        unsubscribed = []
        
        for channel in channels:
            channel_id = channel['channel_id']
            
            try:
                member = await bot.get_chat_member(int(channel_id), user_id)
                
                if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                    unsubscribed.append(channel_id)
                    
            except Exception as e:
                logger.error(f"❌ Failed to check subscription for channel {channel_id}: {e}")
                unsubscribed.append(channel_id)
        
        all_subscribed = len(unsubscribed) == 0
        
        if all_subscribed:
            await user_repo.update_subscription(user_id, True)
        
        return all_subscribed, unsubscribed
    
    async def mark_subscribed(self, user_id: int) -> bool:
        return await user_repo.update_subscription(user_id, True)


subscription_service = SubscriptionService()
