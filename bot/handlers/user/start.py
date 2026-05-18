# bot/handlers/user/start.py
"""Start command handler with registration pipeline."""

import logging
from typing import Optional

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.database.repositories.user_repo import user_repo
from bot.database.repositories.balance_repo import balance_repo
from bot.services.fraud.fraud_service import fraud_service
from bot.services.channel.channel_service import channel_service
from bot.keyboards.user.main_menu import get_main_keyboard
from bot.keyboards.user.captcha import get_captcha_keyboard
from bot.keyboards.user.gender import get_gender_keyboard
from bot.config import settings
from bot.utils.common.timezone import now_str

from bot.handlers.registration.captcha import check_captcha
from bot.handlers.registration.gender import check_gender
from bot.handlers.registration.subscription import check_subscription, ask_subscription

logger = logging.getLogger(__name__)
router = Router(name="start")


# ===================== YORDAMCHI FUNKSIYALAR =====================

async def extract_referrer_id(message: Message, user_id: int) -> Optional[int]:
    """
    Extract and validate referrer ID from /start command.
    
    Args:
        message: Message object
        user_id: New user ID
    
    Returns:
        int or None: Valid referrer ID or None
    """
    args = message.text.split()
    
    if len(args) <= 1:
        return None
    
    try:
        ref_id = int(args[1])

        # Reject IDs outside the valid Telegram user range
        if not (0 < ref_id < 10_000_000_000):
            logger.warning(f"⚠️ Out-of-range referrer ID ignored: {ref_id}")
            return None

        # Self-referral check
        if ref_id == user_id:
            logger.warning(f"❌ Self-referral attempt: {user_id}")
            await message.answer(
                "❌ <b>Xatolik!</b>\n\nO'zingizni taklif qila olmaysiz.",
                parse_mode="HTML"
            )
            return None
        
        # Check if referrer exists
        referrer = await user_repo.get_by_id(ref_id)
        if not referrer:
            logger.warning(f"❌ Referrer not found: {ref_id}")
            await message.answer(
                "❌ <b>Xatolik!</b>\n\nBu referral havola noto'g'ri.",
                parse_mode="HTML"
            )
            return None
        
        # Check if referrer is blocked
        if referrer.get('is_blocked'):
            logger.warning(f"❌ Referrer blocked: {ref_id}")
            await message.answer(
                "❌ <b>Xatolik!</b>\n\nBu foydalanuvchi bloklangan.",
                parse_mode="HTML"
            )
            return None
        
        return ref_id
        
    except (ValueError, IndexError):
        logger.warning(f"⚠️ Invalid referrer format: {message.text}")
        return None


async def is_registration_complete(user_id: int) -> tuple[bool, Optional[str]]:
    """
    Check if user completed all registration steps.
    
    Returns:
        tuple[bool, Optional[str]]: (is_complete, next_step)
        next_step: 'captcha', 'gender', 'phone', 'subscription' or None
    """
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        return False, None
    
    # Check captcha
    if not user.get('captcha_passed') and not settings.test_mode:
        logger.debug(f"User {user_id} needs captcha")
        return False, 'captcha'
    
    # Check gender
    if not user.get('gender'):
        logger.debug(f"User {user_id} needs gender")
        return False, 'gender'

    # Check subscription — ikkala jadval (channels + managed_chats) tekshiriladi
    from bot.utils.subscription_checker import subscription_checker
    all_channels = await subscription_checker.get_all_mandatory_channels()
    if all_channels and not user.get('is_subscribed'):
        logger.debug(f"User {user_id} needs subscription")
        return False, 'subscription'
    
    return True, None


# ===================== START KOMANDASI =====================

@router.message(CommandStart())
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """
    Handle /start command with registration pipeline.
    
    Flow:
    1. Rate limit check
    2. User creation (if new)
    3. Registration completeness check
    4. Redirect to incomplete steps
    5. Show main menu
    """
    user_id = message.from_user.id
    username = message.from_user.username or "username_yoq"
    fullname = message.from_user.full_name
    
    logger.info(f"📨 /start from {user_id} (@{username})")
    
    try:
        # ========== 1. RATE LIMIT CHECK ==========
        # ✅ Yangi (to'g'ri) - 4 ta argument
        is_allowed = await fraud_service.check_rate_limit(user_id, "start_command", 5, 1)
        if not is_allowed:
            await message.answer(
                "⚠️ <b>Juda ko'p so'rov!</b>\n\n"
                "Iltimos, biroz kuting va qaytadan urinib ko'ring.",
                parse_mode="HTML"
            )
            return
        
        # ========== 2. CHECK IF USER EXISTS ==========
        user = await user_repo.get_by_id(user_id)
        
        if not user:
            # ========== NEW USER - CREATE ACCOUNT ==========
            referrer_id = await extract_referrer_id(message, user_id)
            
            success = await user_repo.create(
                user_id=user_id,
                username=username,
                fullname=fullname,
                phone=None,
                referred_by=referrer_id,
                registration_date=now_str()
            )
            
            if not success:
                await message.answer(
                    f"❌ <b>Xatolik yuz berdi!</b>\n\n"
                    f"Iltimos, qaytadan urinib ko'ring.\n\n"
                    f"Muammo davom etsa, admin bilan bog'lang: {settings.admin_mention}",
                    parse_mode="HTML"
                )
                return
            
            logger.info(f"✅ New user created: {user_id} (referred_by: {referrer_id})")
            await state.update_data(referred_by=referrer_id)
            
            # TEST MODE: Skip captcha
            if settings.test_mode:
                logger.info(f"🧪 TEST MODE: Auto-passing captcha for {user_id}")
                await user_repo.update(user_id, {'captcha_passed': True})
                
                await message.answer(
                    "🧪 <b>TEST MODE</b>\n\n"
                    "Captcha avtomatik o'tkazildi!\n\n"
                    "👇 Iltimos, jinsingizni tanlang:",
                    reply_markup=get_gender_keyboard(),
                    parse_mode="HTML"
                )
                return
            
            # Show captcha for new user
            await message.answer(
                "🔐 <b>XAVFSIZLIK TEKSHIRUVI</b>\n\n"
                "Botdan foydalanishni davom ettirish uchun captcha tekshiruvidan o'ting.\n\n"
                "👇 Quyidagi tugmani bosing:",
                reply_markup=get_captcha_keyboard(settings.captcha_web_app_url),
                parse_mode="HTML"
            )
            return
        
        # ========== 3. EXISTING USER - CHECK BLOCK STATUS ==========
        if user.get('is_blocked'):
            await message.answer(
                f"🚫 <b>AKKAUNTINGIZ BLOKLANGAN!</b>\n\n"
                f"Sizning akkauntingiz admin tomonidan bloklangan.\n\n"
                f"Savollaringiz bo'lsa, admin bilan bog'lang: {settings.admin_mention}",
                parse_mode="HTML"
            )
            return
        
        # ========== 4. CHECK REGISTRATION COMPLETENESS ==========
        is_complete, next_step = await is_registration_complete(user_id)
        
        if not is_complete:
            # Redirect to incomplete step
            if next_step == 'captcha':
                await message.answer(
                    "🔐 <b>XAVFSIZLIK TEKSHIRUVI</b>\n\n"
                    "Botdan foydalanishni davom ettirish uchun captcha tekshiruvidan o'ting.\n\n"
                    "👇 Quyidagi tugmani bosing:",
                    reply_markup=get_captcha_keyboard(settings.captcha_web_app_url),
                    parse_mode="HTML"
                )
                return
            
            elif next_step == 'gender':
                await message.answer(
                    "👤 <b>JINS</b>\n\n"
                    "Iltimos, jinsingizni tanlang:",
                    reply_markup=get_gender_keyboard(),
                    parse_mode="HTML"
                )
                return
            
            elif next_step == 'subscription':
                await ask_subscription(message, state)
                return
        
        # ========== 5. UPDATE LAST ACTIVITY ==========
        await user_repo.update_last_activity(user_id, now_str())
        
        # Clear any pending state
        await state.clear()
        
        # Get user balance for welcome message
        balance = await balance_repo.get_balance(user_id)
        
        # ========== 6. SHOW MAIN MENU ==========
        welcome_text = f"""
✅ <b>Xush kelibsiz, {fullname}!</b>

🎉 Siz muvaffaqiyatli ro'yxatdan o'tdingiz!

━━━━━━━━━━━━━━━━━━━━
📌 <b>Bot imkoniyatlari:</b>
• 💎 <b>Referral tizimi</b> - Do'stlaringizni taklif qiling
• ⭐️ <b>Premium va Stars</b> - Arzon narxlarda xarid qiling
• 🎁 <b>Bonuslar</b> - Har kuni bonus oling
• 📊 <b>TOP reyting</b> - Eng faol foydalanuvchilar

━━━━━━━━━━━━━━━━━━━━
💰 <b>Sizning balansingiz:</b> {float(balance):.2f} 💎

━━━━━━━━━━━━━━━━━━━━
💡 <b>Boshlash uchun:</b>
• "✨BEPUL PREMIUM OLISH💫" - Do'stlaringizni taklif qiling
• "💳Mening hisobim" - Balans va statistikangizni ko'ring
• "👑TOP reyting" - Reytingda qatnashing

━━━━━━━━━━━━━━━━━━━━
📞 <b>Admin bilan bog'lanish:</b> {settings.admin_mention}
"""
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_keyboard(is_admin=settings.is_admin(message.from_user.id)),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"❌ Start handler error: {e}", exc_info=True)
        await message.answer(
            f"❌ <b>Texnik xatolik yuz berdi!</b>\n\n"
            f"Iltimos, /start buyrug'ini qaytadan bosing.\n\n"
            f"Muammo davom etsa, admin bilan bog'lang: {settings.admin_mention}",
            parse_mode="HTML"
        )


# ===================== ASOSIY MENYUGA QAYTISH =====================

@router.message(F.text == "🔙 Asosiy menyu")
async def back_to_main_menu(message: Message, state: FSMContext):
    """Return to main menu."""
    user_id = message.from_user.id
    fullname = message.from_user.full_name
    
    # Clear state
    await state.clear()
    
    # Update last activity
    await user_repo.update_last_activity(user_id, now_str())
    
    # Get balance
    balance = await balance_repo.get_balance(user_id)
    
    text = f"""
✅ <b>Asosiy menyu</b>

👋 Xush kelibsiz, {fullname}!
💰 Balansingiz: {float(balance):.2f} 💎
"""
    
    await message.answer(
        text,
        reply_markup=get_main_keyboard(is_admin=settings.is_admin(message.from_user.id)),
        parse_mode="HTML"
    )


# ===================== BEKOR QILISH =====================

@router.message(Command("cancel"))
@router.message(F.text == "/cancel")
async def cancel_handler(message: Message, state: FSMContext):
    """Cancel current operation."""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "❌ <b>Bekor qilinadigan jarayon yo'q</b>\n\n"
            "Siz asosiy menyudasiz.",
            reply_markup=get_main_keyboard(is_admin=settings.is_admin(message.from_user.id)),
            parse_mode="HTML"
        )
        return
    
    await state.clear()
    await message.answer(
        "✅ <b>Jarayon bekor qilindi</b>\n\n"
        "Asosiy menyuga qaytdingiz.",
        reply_markup=get_main_keyboard(is_admin=settings.is_admin(message.from_user.id)),
        parse_mode="HTML"
    )


# ===================== EKSPORT =====================

__all__ = ["router", "cmd_start", "back_to_main_menu", "cancel_handler"]