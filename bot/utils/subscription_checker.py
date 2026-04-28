"""
Subscription check utility - clean separation of concerns.
Handles checking user subscriptions across all mandatory channels.
"""

import logging
import asyncio
from typing import Optional, List, Dict
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.repositories.channel_repo import channel_repo
from bot.database.repositories.join_request_repo import join_request_repo

logger = logging.getLogger(__name__)


class SubscriptionChecker:
    """Service for checking user subscriptions to mandatory channels."""
    
    async def get_all_mandatory_channels(self) -> List[Dict]:
        """
        Get all mandatory channels from both databases.
        
        Returns:
            List of channel dicts with channel_id, channel_name, channel_url
        """
        all_channels = []
        
        try:
            # 1. Public channels (channels table)
            public_channels = await channel_repo.get_all()
            
            if public_channels:
                for ch in public_channels:
                    try:
                        channel_id = ch.get('channel_id')
                        channel_name = ch.get('channel_name', 'Kanal')
                        channel_url = ch.get('channel_url')
                        
                        if channel_id:
                            # Generate URL if not exists
                            if not channel_url:
                                username = channel_id.lstrip('@')
                                channel_url = f"https://t.me/{username}"
                            
                            all_channels.append({
                                'channel_id': channel_id,
                                'channel_name': channel_name,
                                'channel_url': channel_url,
                                'type': 'public'
                            })
                    except Exception as e:
                        logger.debug(f"Public channel parse error: {e}")
                        continue
            
            # 2. Join request channels (managed_chats table)
            managed_chats = await join_request_repo.get_all_active_chats()
            
            if managed_chats:
                for ch in managed_chats:
                    try:
                        chat_id = ch.get('chat_id')
                        fullname = ch.get('fullname', 'Chat')
                        invite_link = ch.get('invite_link')
                        
                        if chat_id:
                            # Generate invite link if not exists
                            if not invite_link:
                                chat_id_clean = str(chat_id).replace('-100', '')
                                invite_link = f"https://t.me/c/{chat_id_clean}"
                            
                            all_channels.append({
                                'channel_id': chat_id,
                                'channel_name': fullname,
                                'channel_url': invite_link,
                                'type': 'managed'
                            })
                    except Exception as e:
                        logger.debug(f"Managed chat parse error: {e}")
                        continue
            
            logger.info(
                f"📊 Total mandatory channels: {len(all_channels)} "
                f"(public: {len(public_channels) if public_channels else 0}, "
                f"managed: {len(managed_chats) if managed_chats else 0})"
            )
            
            return all_channels
            
        except Exception as e:
            logger.error(f"❌ get_all_mandatory_channels error: {e}", exc_info=True)
            return []
    
    async def check_single_channel(
        self, 
        bot: Bot, 
        user_id: int, 
        channel: Dict
    ) -> Dict:
        """
        Check if user is subscribed to a single channel.
        
        Args:
            bot: Bot instance
            user_id: User ID
            channel: Channel dict
        
        Returns:
            Dict with subscription status and channel info
        """
        try:
            channel_id = channel['channel_id']
            channel_name = channel['channel_name']
            channel_url = channel['channel_url']
            
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            
            is_subscribed = member.status not in ["left", "kicked"]
            
            if not is_subscribed:
                logger.info(f"❌ User {user_id} not subscribed to {channel_name}")
            
            return {
                'subscribed': is_subscribed,
                'channel_id': channel_id,
                'channel_name': channel_name,
                'channel_url': channel_url,
                'type': channel.get('type', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"❌ Channel {channel.get('channel_id')} check error: {e}")
            # Default to not subscribed for safety
            return {
                'subscribed': False,
                'channel_id': channel.get('channel_id'),
                'channel_name': channel.get('channel_name', 'Unknown'),
                'channel_url': channel.get('channel_url', ''),
                'type': channel.get('type', 'unknown')
            }
    
    async def get_subscription_keyboard(
        self, 
        bot: Bot, 
        user_id: int
    ) -> Optional[InlineKeyboardMarkup]:
        """
        Get subscription keyboard if user is not subscribed to all channels.
        Uses parallel API calls for performance.
        
        Args:
            bot: Bot instance
            user_id: User ID
        
        Returns:
            InlineKeyboardMarkup if subscription needed, None otherwise
        """
        try:
            channels = await self.get_all_mandatory_channels()
            
            if not channels:
                logger.warning("⚠️ No mandatory channels in database!")
                return None
            
            # Parallel check all channels
            tasks = [
                self.check_single_channel(bot, user_id, ch) 
                for ch in channels
            ]
            results = await asyncio.gather(*tasks)
            
            # Build keyboard for unsubscribed channels
            keyboard = []
            not_subscribed = False
            
            for result in results:
                if not result['subscribed']:
                    not_subscribed = True
                    keyboard.append([
                        InlineKeyboardButton(
                            text=f"➕ {result['channel_name']}", 
                            url=result['channel_url']
                        )
                    ])
            
            if not_subscribed:
                keyboard.append([
                    InlineKeyboardButton(
                        text="✅ Obunalarni tekshirish", 
                        callback_data="check_subscription"
                    )
                ])
                
                logger.info(f"⚠️ User {user_id} needs to subscribe to {len([r for r in results if not r['subscribed']])} channels")
                return InlineKeyboardMarkup(inline_keyboard=keyboard)
            
            logger.info(f"✅ User {user_id} subscribed to all channels")
            return None
            
        except Exception as e:
            logger.error(f"❌ get_subscription_keyboard error: {e}", exc_info=True)
            return InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="🔄 Qayta urinish", 
                    callback_data="check_subscription"
                )
            ]])
    
    async def check_user_subscriptions(self, bot: Bot, user_id: int) -> bool:
        """
        Check if user is subscribed to all mandatory channels.
        Uses parallel API calls for performance.
        
        Args:
            bot: Bot instance
            user_id: User ID
        
        Returns:
            True if subscribed to all, False otherwise
        """
        try:
            channels = await self.get_all_mandatory_channels()
            
            if not channels:
                return True  # No mandatory channels = always subscribed
            
            # Parallel check
            tasks = [
                self.check_single_channel(bot, user_id, ch) 
                for ch in channels
            ]
            results = await asyncio.gather(*tasks)
            
            # All must be subscribed
            all_subscribed = all(r['subscribed'] for r in results)
            
            if not all_subscribed:
                unsubscribed_count = sum(1 for r in results if not r['subscribed'])
                logger.info(f"⚠️ User {user_id} not subscribed to {unsubscribed_count} channels")
            
            return all_subscribed
            
        except Exception as e:
            logger.error(f"❌ check_user_subscriptions error: {e}", exc_info=True)
            return False
    
    async def get_unsubscribed_channels(
        self, 
        bot: Bot, 
        user_id: int
    ) -> List[Dict]:
        """
        Get list of channels user is not subscribed to.
        Uses parallel API calls for performance.
        
        Args:
            bot: Bot instance
            user_id: User ID
        
        Returns:
            List of unsubscribed channel dicts
        """
        try:
            channels = await self.get_all_mandatory_channels()
            
            if not channels:
                return []
            
            # Parallel check
            tasks = [
                self.check_single_channel(bot, user_id, ch) 
                for ch in channels
            ]
            results = await asyncio.gather(*tasks)
            
            # Filter only unsubscribed
            unsubscribed = [r for r in results if not r['subscribed']]
            
            logger.info(f"📊 User {user_id} not subscribed to {len(unsubscribed)} channels")
            return unsubscribed
            
        except Exception as e:
            logger.error(f"❌ get_unsubscribed_channels error: {e}")
            return []


# Singleton instance
subscription_checker = SubscriptionChecker()


__all__ = ["subscription_checker", "SubscriptionChecker"]
