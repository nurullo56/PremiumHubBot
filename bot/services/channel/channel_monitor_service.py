# bot/services/channel/channel_monitor_service.py
"""
Channel monitor service - BUSINESS LOGIC ONLY
No direct DB operations here!
"""

import asyncio
import logging
import time
from decimal import Decimal
from typing import Optional, Tuple
from dataclasses import dataclass

from aiogram import Bot

from bot.database.repositories.channel_monitor_repo import channel_monitor_repo
from bot.config.constants import CHANNEL_LEAVE_DEDUCTION, MAX_BONUS_RETURNS_PER_DAY
from bot.utils.common.timezone import now_str

logger = logging.getLogger(__name__)

BONUS_RETURN_AMOUNT = Decimal(str(CHANNEL_LEAVE_DEDUCTION))  # 0.2 olmos har kanal uchun


@dataclass
class BonusReturnResult:
    """Bonus return operation result."""
    success: bool
    user_id: int
    referrer_id: int
    amount: Decimal
    new_balance: Decimal
    reason: Optional[str] = None
    duration_ms: float = 0.0


class ChannelMonitorService:
    """
    Service for channel monitoring and bonus return.
    No direct DB access - uses repository and balance_service.
    """

    def __init__(self):
        self.repo = channel_monitor_repo

    async def is_mandatory_channel(
        self, chat_id: int, chat_username: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Check if channel is mandatory. Returns (is_mandatory, channel_name)."""
        channels = await self.repo.get_mandatory_channels()
        chat_id_str = str(chat_id)

        for channel in channels:
            db_channel_id = str(channel.get('channel_id', ''))

            if db_channel_id == chat_id_str:
                return True, channel.get('channel_name', 'Kanal')

            if chat_username:
                clean_username = chat_username.lstrip('@').lower()
                db_username = db_channel_id.lstrip('@').lower()
                if db_username == clean_username:
                    return True, channel.get('channel_name', 'Kanal')

        return False, None

    async def process_bonus_return(
        self,
        user_id: int,
        channel_id: str,
        channel_name: str,
        bot: Bot
    ) -> BonusReturnResult:
        """
        Process bonus return when user leaves mandatory channel.

        Uses balance_service.subtract_balance() for atomic balance update + history
        in a single transaction (BEGIN IMMEDIATE + RETURNING).
        """
        # Lazy import avoids circular dependency at module load time
        from bot.services.finance.balance_service import balance_service

        start_time = time.time()

        try:
            # 1. Get user
            user = await self.repo.get_user_by_id(user_id)
            if not user:
                return BonusReturnResult(
                    success=False, user_id=user_id, referrer_id=0,
                    amount=Decimal('0'), new_balance=Decimal('0'),
                    reason="User not found"
                )

            # 2. Check referrer
            referrer_id = user.get('referred_by')
            if not referrer_id:
                return BonusReturnResult(
                    success=False, user_id=user_id, referrer_id=0,
                    amount=Decimal('0'), new_balance=Decimal('0'),
                    reason="No referrer"
                )

            # 3. Dastlabki bonus berilganmi?
            if not user.get('referral_bonus_given'):
                return BonusReturnResult(
                    success=False, user_id=user_id, referrer_id=referrer_id,
                    amount=Decimal('0'), new_balance=Decimal('0'),
                    reason="Bonus not given yet"
                )

            # 4. Bu kanal uchun allaqachon ayrilganmi?
            already_deducted = await self.repo.is_channel_bonus_deducted(user_id, channel_id)
            if already_deducted:
                return BonusReturnResult(
                    success=False, user_id=user_id, referrer_id=referrer_id,
                    amount=Decimal('0'), new_balance=Decimal('0'),
                    reason=f"Already deducted for channel {channel_id}"
                )

            # 5. Rate limit
            today_returns = await self.repo.get_today_bonus_returns_count(referrer_id)
            if today_returns >= MAX_BONUS_RETURNS_PER_DAY:
                return BonusReturnResult(
                    success=False, user_id=user_id, referrer_id=referrer_id,
                    amount=Decimal('0'), new_balance=Decimal('0'),
                    reason=f"Rate limit exceeded (max {MAX_BONUS_RETURNS_PER_DAY}/day)"
                )

            # 6. 0.2 olmos ayirish
            user_fullname = user.get('fullname', 'User')
            deducted, _, new_balance = await balance_service.subtract_balance(
                user_id=referrer_id,
                amount=BONUS_RETURN_AMOUNT,
                description=f"-{BONUS_RETURN_AMOUNT}💎: {user_fullname} «{channel_name}» dan chiqdi",
                transaction_type="bonus_return"
            )

            if not deducted:
                new_balance = await balance_service.get_balance(referrer_id)
                logger.warning(f"⚠️ Insufficient balance for deduction: referrer={referrer_id}")

            # 7. Bu kanal uchun ayrilganligini belgilash + is_subscribed=0
            await self.repo.mark_channel_bonus_deducted(user_id, channel_id)
            await self.repo.reset_user_subscription(user_id)

            # 7. Audit log
            timestamp = now_str()
            await self.repo.log_channel_leave(
                user_id=user_id,
                channel_id=channel_id,
                channel_name=channel_name,
                referrer_id=referrer_id,
                bonus_returned=1 if deducted else 0,
                returned_at=timestamp
            )

            duration_ms = (time.time() - start_time) * 1000
            logger.warning(
                f"💰 Bonus return: referrer={referrer_id}, user={user_id}, "
                f"deducted={deducted}, amount={BONUS_RETURN_AMOUNT}, "
                f"new_balance={new_balance}, duration={duration_ms:.2f}ms"
            )

            # 8. Notify referrer (fire-and-forget, outside the DB transaction)
            asyncio.create_task(
                self._send_notification(
                    bot, referrer_id, user_id,
                    user_fullname, channel_name, new_balance
                )
            )

            return BonusReturnResult(
                success=True,
                user_id=user_id,
                referrer_id=referrer_id,
                amount=BONUS_RETURN_AMOUNT if deducted else Decimal('0'),
                new_balance=new_balance,
                duration_ms=duration_ms
            )

        except Exception as e:
            logger.error(f"❌ process_bonus_return error: {e}", exc_info=True)
            return BonusReturnResult(
                success=False, user_id=user_id, referrer_id=0,
                amount=Decimal('0'), new_balance=Decimal('0'),
                reason=str(e)
            )

    async def _send_notification(
        self,
        bot: Bot,
        referrer_id: int,
        user_id: int,
        user_name: str,
        channel_name: str,
        new_balance: Decimal
    ) -> None:
        """Send notification to referrer (called as fire-and-forget task)."""
        try:
            text = (
                f"⚠️ <b>OGOHLANTIRISH!</b>\n\n"
                f"👤 <b>{user_name}</b> kanaldan chiqdi!\n"
                f"📢 Kanal: <b>{channel_name}</b>\n"
                f"💎 <b>-{BONUS_RETURN_AMOUNT} olmos</b> yechildi.\n\n"
                f"💰 Balansingiz: <b>{new_balance:.2f} olmos</b>\n\n"
                f"💡 Do'stingiz qayta kirsa bonus qaytariladi!"
            )
            await bot.send_message(referrer_id, text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Failed to send bonus-return notification to {referrer_id}: {e}")


# Singleton
channel_monitor_service = ChannelMonitorService()

__all__ = ["channel_monitor_service", "ChannelMonitorService", "BonusReturnResult"]
