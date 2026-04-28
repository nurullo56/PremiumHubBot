# bot/services/admin/broadcast_service.py
"""Broadcast service for sending messages to users."""

import logging
import asyncio
from typing import Dict, Any, List
from aiogram import Bot
from aiogram.types import Message

from bot.database.uow.uow import UnitOfWork

logger = logging.getLogger(__name__)


class BroadcastService:
    """Service for sending broadcast messages."""
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        async with UnitOfWork() as uow:
            return await uow.users.get_all(limit=1000000)  # Get all
    
    async def get_all_user_ids(self) -> List[int]:
        """Get all user IDs."""
        async with UnitOfWork() as uow:
            rows = await uow.users.fetch_all(
                "SELECT user_id FROM users WHERE is_blocked = 0"
            )
            return [row['user_id'] for row in rows]
    
    async def get_premium_user_ids(self) -> List[int]:
        """Get premium user IDs."""
        async with UnitOfWork() as uow:
            rows = await uow.users.fetch_all(
                "SELECT user_id FROM users WHERE premium_status IN ('active', 'approved') AND is_blocked = 0"
            )
            return [row['user_id'] for row in rows]
    
    async def send_broadcast(
        self, 
        bot: Bot, 
        message_text: str, 
        delay: float = 0.05
    ) -> Dict[str, int]:
        """
        Send broadcast to all users.
        
        Args:
            bot: Bot instance
            message_text: Text to send
            delay: Delay between messages (seconds)
        
        Returns:
            Dict with sent, failed, blocked counts
        """
        user_ids = await self.get_all_user_ids()
        return await self._send_to_users(bot, user_ids, message_text, delay)
    
    async def send_to_premium_users(
        self, 
        bot: Bot, 
        message_text: str, 
        delay: float = 0.05
    ) -> Dict[str, int]:
        """Send broadcast to premium users only."""
        user_ids = await self.get_premium_user_ids()
        return await self._send_to_users(bot, user_ids, message_text, delay)
    
    async def _send_to_users(
        self, 
        bot: Bot, 
        user_ids: List[int], 
        message_text: str, 
        delay: float
    ) -> Dict[str, int]:
        """Send message to specific users."""
        stats = {
            'sent': 0,
            'failed': 0,
            'blocked': 0
        }
        
        total = len(user_ids)
        
        for i, user_id in enumerate(user_ids, 1):
            try:
                await bot.send_message(user_id, message_text, parse_mode="HTML")
                stats['sent'] += 1
                
                # Progress log every 100 users
                if i % 100 == 0:
                    logger.info(f"📤 Broadcast progress: {i}/{total} ({stats['sent']} sent)")
                
                # Small delay to avoid rate limits
                await asyncio.sleep(delay)
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "blocked" in error_msg or "deactivated" in error_msg:
                    stats['blocked'] += 1
                    logger.warning(f"User {user_id} blocked bot")
                    
                    # Optionally mark user as blocked in database
                    async with UnitOfWork() as uow:
                        await uow.users.block_user(user_id)
                        await uow.commit()
                else:
                    stats['failed'] += 1
                    logger.error(f"Failed to send to {user_id}: {e}")
        
        logger.info(f"✅ Broadcast completed: sent={stats['sent']}, failed={stats['failed']}, blocked={stats['blocked']}")
        return stats


# Singleton instance
broadcast_service = BroadcastService()