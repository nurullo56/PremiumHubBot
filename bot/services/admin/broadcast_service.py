# bot/services/admin/broadcast_service.py
"""Broadcast service for sending messages to users."""

import logging
import asyncio
from typing import Dict, List, Optional
from aiogram import Bot

from bot.database.base import get_db
from bot.database.repositories.user_repo import user_repo

logger = logging.getLogger(__name__)


class BroadcastService:

    async def get_user_ids(
        self,
        target: str = "all"
    ) -> List[Dict]:
        """
        Get users based on target filter.
        Returns list of dicts with user_id and fullname.

        target: "all" | "male" | "female" | "premium"
        """
        try:
            async with get_db() as db:
                if target == "male":
                    q = "SELECT user_id, fullname FROM users WHERE gender = 'male' AND is_blocked = 0"
                elif target == "female":
                    q = "SELECT user_id, fullname FROM users WHERE gender = 'female' AND is_blocked = 0"
                elif target == "premium":
                    q = ("SELECT user_id, fullname FROM users "
                         "WHERE premium_status IN ('active', 'approved') AND is_blocked = 0")
                else:
                    q = "SELECT user_id, fullname FROM users WHERE is_blocked = 0"

                cursor = await db.execute(q)
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"❌ get_user_ids error (target={target}): {e}")
            return []

    async def send_broadcast(
        self,
        bot: Bot,
        message_text: str,
        target: str = "all",
        delay: float = 0.05
    ) -> Dict[str, int]:
        """
        Send broadcast to users.
        Supports {fullname} placeholder in message_text — replaced per user.
        """
        users = await self.get_user_ids(target)
        return await self._send_to_users(bot, users, message_text, delay)

    async def send_media_broadcast(
        self,
        bot: Bot,
        file_id: str,
        content_type: str,
        caption: str = "",
        target: str = "all",
        delay: float = 0.05
    ) -> Dict[str, int]:
        """Send photo/video broadcast. Supports {fullname} in caption."""
        users = await self.get_user_ids(target)
        return await self._send_media_to_users(bot, users, file_id, content_type, caption, delay)

    async def _send_media_to_users(
        self,
        bot: Bot,
        users: List[Dict],
        file_id: str,
        content_type: str,
        caption: str,
        delay: float
    ) -> Dict[str, int]:
        stats = {'sent': 0, 'failed': 0, 'blocked': 0}
        total = len(users)

        for i, u in enumerate(users, 1):
            uid = u['user_id']
            fullname = u.get('fullname') or 'Foydalanuvchi'
            text = caption.replace('{fullname}', fullname)

            try:
                if content_type == "photo":
                    await bot.send_photo(uid, file_id, caption=text, parse_mode="HTML")
                elif content_type == "video":
                    await bot.send_video(uid, file_id, caption=text, parse_mode="HTML")
                stats['sent'] += 1
                if i % 100 == 0:
                    logger.info(f"📤 Media broadcast: {i}/{total}")
                await asyncio.sleep(delay)
            except Exception as e:
                err = str(e).lower()
                if "blocked" in err or "deactivated" in err or "forbidden" in err:
                    stats['blocked'] += 1
                    await user_repo.block_user(uid)
                else:
                    stats['failed'] += 1
                    logger.error(f"Failed media send to {uid}: {e}")

        return stats

    async def _send_to_users(
        self,
        bot: Bot,
        users: List[Dict],
        message_text: str,
        delay: float
    ) -> Dict[str, int]:
        stats = {'sent': 0, 'failed': 0, 'blocked': 0}
        total = len(users)

        for i, u in enumerate(users, 1):
            uid = u['user_id']
            fullname = u.get('fullname') or 'Foydalanuvchi'

            # Replace {fullname} placeholder with actual name
            text = message_text.replace('{fullname}', fullname)

            try:
                await bot.send_message(uid, text, parse_mode="HTML")
                stats['sent'] += 1

                if i % 100 == 0:
                    logger.info(f"📤 Broadcast: {i}/{total} ({stats['sent']} sent)")

                await asyncio.sleep(delay)

            except Exception as e:
                err = str(e).lower()
                if "blocked" in err or "deactivated" in err or "forbidden" in err:
                    stats['blocked'] += 1
                    await user_repo.block_user(uid)
                    logger.warning(f"User {uid} blocked bot — marked blocked")
                else:
                    stats['failed'] += 1
                    logger.error(f"Failed to send to {uid}: {e}")

        logger.info(
            f"✅ Broadcast done: sent={stats['sent']}, "
            f"failed={stats['failed']}, blocked={stats['blocked']}"
        )
        return stats


broadcast_service = BroadcastService()
