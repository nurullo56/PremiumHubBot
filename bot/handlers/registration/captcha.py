# bot/handlers/registration/captcha.py
"""
Captcha tekshirish va qayta ishlov berish
✅ YANGI STRUKTURAGA MOS
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from bot.config import settings
from bot.database.repositories.user_repo import user_repo
from bot.keyboards.user.captcha import get_captcha_keyboard
from bot.states.user.registration import RegistrationStates

logger = logging.getLogger(__name__)
router = Router(name="registration_captcha")


async def check_captcha(user_id: int, message: Message) -> bool:
    """
    Captcha tekshirish
    
    Returns:
        True - captcha o'tilgan, davom etish mumkin
        False - captcha kerak, to'xtatish
    """
    logger.info(f"🤖 Captcha tekshiruvi... TEST_MODE={settings.test_mode}")
    
    if settings.test_mode:
        logger.info(f"⏩ Captcha skip (TEST_MODE): {user_id}")
        await user_repo.update(user_id, {'captcha_passed': True})
        return True
    
    user = await user_repo.get_by_id(user_id)
    
    if not user or not user.get('captcha_passed'):
        logger.info(f"⏳ Captcha kerak: {user_id}")
        
        await message.answer(
            "🔐 <b>Xavfsizlik tekshiruvi</b>\n\n"
            "Botdan foydalanish uchun quyidagi tugmani bosing:",
            reply_markup=get_captcha_keyboard(settings.captcha_web_app_url),
            parse_mode="HTML"
        )
        return False
    
    logger.info(f"✅ Captcha o'tilgan: {user_id}")
    return True


@router.message(F.web_app_data)
async def handle_captcha_result(message: Message):
    """Captcha dan kelgan ma'lumot"""
    user_id = message.from_user.id
    
    if message.web_app_data.data == "verified":
        await user_repo.update(user_id, {'captcha_passed': True})
        logger.info(f"✅ Captcha passed: {user_id}")
        
        await message.answer("✅ Xavfsizlik tekshiruvi muvaffaqiyatli!")
        
        # Davom etish uchun gender handleriga o'tish
        from bot.handlers.user.start import cmd_start
        await cmd_start(message)
    else:
        await message.answer("❌ Captcha tekshiruvi xato! Qaytadan urinib ko'ring.")


__all__ = ["router", "check_captcha"]