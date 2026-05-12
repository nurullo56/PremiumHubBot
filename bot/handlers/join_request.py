"""
Join Request Handler - handles chat join requests from users.
Separated from admin handlers for clean architecture.
"""

import logging
from aiogram import Router, Bot
from aiogram.types import ChatJoinRequest

from bot.database.repositories.join_request_repo import join_request_repo
from bot.database.repositories.user_repo import user_repo
from bot.handlers.channel_monitor import _auto_complete_registration

logger = logging.getLogger(__name__)
router = Router(name="join_request_handler")


async def send_welcome_message(
    bot: Bot, 
    user_id: int, 
    chat_name: str, 
    chat_type: str
):
    """
    Send welcome message to user after approval.
    
    Args:
        bot: Bot instance
        user_id: User ID
        chat_name: Chat name
        chat_type: Chat type ('zayavka', 'public', etc.)
    """
    try:
        if chat_type == "zayavka" or chat_type == "managed":
            message = (
                f"✅ <b>Tasdiqlandi!</b>\n\n"
                f"📢 Kanal: <b>{chat_name}</b>\n"
                f"🎉 Siz muvaffaqiyatli qo'shildingiz!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 <b>Keyingi qadam:</b>\n"
                f"1. Botga qayting\n"
                f"2. \"✨BEPUL PREMIUM OLISH💫\" tugmasini bosing\n"
                f"3. Do'stlaringizni taklif qiling va olmos yig'ing!\n\n"
                f"🎁 <b>Bonus:</b> Har bir do'stingiz uchun <b>1.4 olmos</b> olasiz!\n"
                f"🏆 <b>Premium:</b> 40 ta do'st uchun <b>BEPUL Telegram Premium</b>!"
            )
        else:
            message = (
                f"✅ <b>Kanalga qo'shildingiz!</b>\n\n"
                f"📢 Kanal: <b>{chat_name}</b>\n"
                f"🎉 Endi siz kanaldan yangiliklarni o'qishingiz mumkin!\n\n"
                f"💡 Botdan foydalanishni davom eting!"
            )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"✅ Welcome message sent: user={user_id}, chat={chat_name}")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to send welcome message: user={user_id}, error={e}")


async def send_pending_message(bot: Bot, user_id: int, chat_name: str):
    """
    Send pending notification to user.
    
    Args:
        bot: Bot instance
        user_id: User ID
        chat_name: Chat name
    """
    try:
        message = (
            f"📥 <b>So'rov qabul qilindi!</b>\n\n"
            f"📢 Kanal: <b>{chat_name}</b>\n"
            f"⏳ Holat: <b>Kutilmoqda</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 <b>Nima qilish kerak?</b>\n"
            f"• Kanal adminlari so'rovingizni ko'rib chiqmoqda\n"
            f"• Tasdiqlangandan so'ng sizga xabar keladi\n"
            f"• Biroz kuting, tez orada tasdiqlanasiz"
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="HTML"
        )
        logger.info(f"✅ Pending message sent: user={user_id}, chat={chat_name}")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to send pending message: user={user_id}, error={e}")


@router.chat_join_request()
async def handle_join_request(request: ChatJoinRequest, bot: Bot):
    """
    Handle user join request to channel/group.
    
    Workflow:
    1. Get chat type from database
    2. Auto-approve if managed chat (zayavka)
    3. Save request to database
    4. Send notification to user
    """
    user_id = request.from_user.id
    chat_id = str(request.chat.id)
    chat_title = request.chat.title or "Chat"
    username = request.from_user.username or "unknown"
    fullname = request.from_user.full_name
    
    logger.info(
        f"📥 JOIN REQUEST | user={user_id} ({fullname}) @{username} | "
        f"chat={chat_id} ({chat_title})"
    )
    
    try:
        # 1. Get chat info from database
        chat_info = await join_request_repo.get_chat_by_id(chat_id)
        
        chat_type = "unknown"
        chat_name = chat_title
        auto_approve = False
        
        if chat_info:
            chat_type = chat_info.get('chat_type', 'managed')
            chat_name = chat_info.get('fullname', chat_title)
            logger.info(f"📊 Chat type: {chat_type}, name: {chat_name}")
        else:
            # Channel not found by ID — try to find by title and fix the ID.
            chat_by_title = await join_request_repo.get_chat_by_title(chat_title)
            if chat_by_title:
                old_id = chat_by_title['chat_id']
                await join_request_repo.fix_chat_id(old_id, chat_id)
                chat_type = chat_by_title.get('chat_type', 'managed')
                chat_name = chat_by_title.get('fullname', chat_title)
                logger.info(f"🔧 Chat ID corrected: {old_id} → {chat_id}, name: {chat_name}")
            else:
                logger.info(f"ℹ️ Chat {chat_id} not in managed chats database")

        # 2. So'rov saqlanadi — admin o'zi Telegram orqali tasdiqlaydi
        status = "pending"
        approved = False
        
        # 3. Save to database
        try:
            success, msg = await join_request_repo.update_request(
                user_id=user_id,
                chat_id=chat_id,
                has_requested=True,
                status=status
            )
            
            if success:
                logger.info(f"✅ Join request saved: {user_id} -> {chat_name} (status={status})")
            else:
                logger.error(f"❌ Failed to save join request: {msg}")
                
        except Exception as db_error:
            logger.error(f"❌ Database error: {db_error}", exc_info=True)
        
        # 4. Send notification to user
        if approved:
            await send_welcome_message(bot, user_id, chat_name, chat_type)
            # Auto-check: complete registration if all channels now joined
            await _auto_complete_registration(user_id, bot)
        else:
            await send_pending_message(bot, user_id, chat_name)
        
        # 5. Check if user exists in database
        user = await user_repo.get_by_id(user_id)
        if not user:
            logger.info(f"ℹ️ User {user_id} not registered, should use /start")
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        "👋 <b>Botga xush kelibsiz!</b>\n\n"
                        f"Siz <b>{chat_name}</b> kanaliga qo'shildingiz.\n\n"
                        "🎁 <b>Botdan to'liq foydalanish uchun:</b>\n"
                        "1️⃣ /start buyrug'ini bosing\n"
                        "2️⃣ Ro'yxatdan o'ting\n"
                        "3️⃣ Do'stlaringizni taklif qiling va olmos yig'ing!\n\n"
                        "✨ <b>40 ta do'st</b> yig'ib, <b>BEPUL Telegram Premium</b> oling!"
                    ),
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.warning(f"⚠️ Failed to send start message to {user_id}: {e}")
    
    except Exception as e:
        logger.error(f"❌ Join request handler error: {e}", exc_info=True)


__all__ = ["router"]
