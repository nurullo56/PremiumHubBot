# bot/handlers/join_requests.py
"""Join request handler - for private channels/groups."""
import logging
from aiogram import Router, Bot
from aiogram.types import ChatJoinRequest
from bot.database.repositories.join_request_repo import join_request_repo
from bot.services.channel.channel_service import channel_service

logger = logging.getLogger(__name__)
router = Router(name="join_requests")

@router.chat_join_request()
async def handle_join_request(request: ChatJoinRequest, bot: Bot):
    """Handle user join request."""
    user_id = request.from_user.id
    chat_id = str(request.chat.id)
    chat_name = request.chat.title or "Kanal"
    
    logger.info(f"📥 Join request: {user_id} -> {chat_name}")
    
    # Check if auto-approve is enabled for this chat
    channel = await channel_service.get_by_id(chat_id)
    
    if channel and channel.get('auto_approve'):
        await bot.approve_chat_join_request(chat_id=int(chat_id), user_id=user_id)
        logger.info(f"✅ Auto-approved: {user_id} -> {chat_name}")
        
        await bot.send_message(
            user_id,
            f"✅ <b>Tasdiqlandi!</b>\n\n"
            f"📢 Kanal: <b>{chat_name}</b>\n"
            f"🎉 Siz muvaffaqiyatli qo'shildingiz!",
            parse_mode="HTML"
        )
    else:
        # Save to database for manual approval
        await join_request_repo.create(user_id, chat_id, chat_name, "pending")