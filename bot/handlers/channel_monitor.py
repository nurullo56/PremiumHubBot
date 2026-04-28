"""Channel monitor - bonus return system when user leaves mandatory channels."""

import logging
from aiogram import Router, Bot
from aiogram.types import ChatMemberUpdated
from aiogram.filters import IS_NOT_MEMBER, IS_MEMBER, ChatMemberUpdatedFilter

from bot.database.repositories.user_repo import user_repo
from bot.database.repositories.channel_repo import channel_repo
from bot.services.finance.balance_service import balance_service
from bot.services.referral.referral_service import referral_service
from bot.config.constants import REFERRAL_BONUS_AMOUNT

logger = logging.getLogger(__name__)
router = Router(name="channel_monitor")


async def is_mandatory_channel(chat_id: int, chat_username: str = None) -> bool:
    """Check if channel is mandatory."""
    try:
        chat_id_str = str(chat_id)
        
        # Check active channels
        channels = await channel_repo.get_active_channels()
        
        for channel in channels:
            channel_id = str(channel.get('channel_id', ''))
            
            if channel_id == chat_id_str:
                return True
            
            if chat_username:
                clean_username = chat_username.lstrip('@').lower()
                db_username = channel_id.lstrip('@').lower()
                if db_username == clean_username:
                    return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Error checking mandatory channel: {e}")
        return False


async def process_bonus_return(user_id: int, fullname: str, chat_title: str, bot: Bot) -> bool:
    """Return bonus when user leaves mandatory channel."""
    try:
        user = await user_repo.get_by_id(user_id)
        
        if not user or not user.get('referred_by'):
            return False
        
        if not user.get('referral_bonus_given'):
            return False
        
        referrer_id = user['referred_by']
        
        logger.warning(f"🔄 Returning bonus: referrer={referrer_id} <- user={user_id}")
        
        # Subtract balance from referrer
        description = f"Bonus qaytarildi: {fullname} {chat_title} kanalidan chiqdi"
        success = await balance_service.subtract_balance(referrer_id, REFERRAL_BONUS_AMOUNT, description)
        
        if not success:
            return False
        
        # Reset bonus flag
        await user_repo.update(user_id, {'referral_bonus_given': False})
        
        logger.warning(f"✅ Bonus returned: referrer={referrer_id} (-{REFERRAL_BONUS_AMOUNT})")
        
        # Notify referrer
        try:
            message_text = (
                f"⚠️ <b>OGOHLANTIRISH!</b>\n\n"
                f"👤 <b>{fullname}</b> majburiy kanaldan chiqdi!\n"
                f"📢 Kanal: <b>{chat_title}</b>\n"
                f"💎 <b>-{REFERRAL_BONUS_AMOUNT} so'm</b> hisobingizdan yechildi.\n\n"
                f"💡 Do'stingizni qayta kanalga qo'shilishga undang!"
            )
            
            await bot.send_message(referrer_id, message_text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"❌ Failed to notify referrer: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error returning bonus: {e}", exc_info=True)
        return False


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def user_left_channel(event: ChatMemberUpdated):
    """Handle user leaving channel."""
    user_id = event.from_user.id
    chat_id = event.chat.id
    fullname = event.from_user.full_name
    chat_title = event.chat.title or "Kanal"
    chat_username = event.chat.username
    
    logger.warning(f"🚪 User left: user_id={user_id} | chat_id={chat_id}")
    
    try:
        is_mandatory = await is_mandatory_channel(chat_id, chat_username)
        
        if not is_mandatory:
            logger.info(f"⚠️ Not a mandatory channel: {chat_id}")
            return
        
        logger.warning(f"⚠️ LEFT MANDATORY CHANNEL: user={user_id}")
        
        success = await process_bonus_return(user_id, fullname, chat_title, event.bot)
        
        if success:
            logger.warning(f"✅ Bonus successfully returned: user={user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error in left channel handler: {e}", exc_info=True)


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def user_joined_channel(event: ChatMemberUpdated):
    """Handle user joining channel."""
    user_id = event.from_user.id
    chat_id = event.chat.id
    chat_username = event.chat.username
    chat_title = event.chat.title or "Kanal"
    
    logger.info(f"👋 User joined: user_id={user_id} | chat_id={chat_id}")
    
    try:
        is_mandatory = await is_mandatory_channel(chat_id, chat_username)
        
        if not is_mandatory:
            return
        
        logger.info(f"✅ Joined mandatory channel: user={user_id}")
        
        # Send welcome message
        try:
            message_text = (
                f"👋 <b>Xush kelibsiz!</b>\n\n"
                f"Siz <b>{chat_title}</b> kanaliga qo'shildingiz.\n\n"
                f"💡 Kanalda qolish orqali bonuslaringizni saqlab qolasiz!"
            )
            
            await event.bot.send_message(user_id, message_text, parse_mode="HTML")
        except Exception as e:
            logger.warning(f"⚠️ Failed to send welcome: {e}")
        
    except Exception as e:
        logger.error(f"❌ Error in joined channel handler: {e}", exc_info=True)
