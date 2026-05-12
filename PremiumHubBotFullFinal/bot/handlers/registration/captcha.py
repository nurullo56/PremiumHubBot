# bot/handlers/registration/captcha.py
"""Captcha tekshirish va qayta ishlov berish."""

import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.config import settings
from bot.database.repositories.user_repo import user_repo
from bot.keyboards.user.captcha import get_captcha_keyboard

logger = logging.getLogger(__name__)
router = Router(name="registration_captcha")


async def check_captcha(user_id: int, message: Message) -> bool:
    """
    Captcha tekshirish.
    True  — o'tilgan, davom etish mumkin.
    False — kerak, to'xtatish.
    """
    if settings.test_mode:
        logger.info(f"⏩ Captcha skip (TEST_MODE): {user_id}")
        await user_repo.update(user_id, {'captcha_passed': True})
        return True

    user = await user_repo.get_by_id(user_id)

    if not user or not user.get('captcha_passed'):
        logger.info(f"⏳ Captcha kerak: {user_id}")
        await message.answer(
            "🔐 <b>Xavfsizlik tekshiruvi</b>\n\n"
            "Botdan foydalanish uchun quyidagi tugmani bosing va "
            "matematik masalani yechilg:",
            reply_markup=get_captcha_keyboard(settings.captcha_web_app_url),
            parse_mode="HTML"
        )
        return False

    return True


@router.message(F.web_app_data)
async def handle_captcha_result(message: Message, state: FSMContext):
    """WebApp dan kelgan natija."""
    user_id = message.from_user.id

    if message.web_app_data.data == "verified":
        await user_repo.update(user_id, {'captcha_passed': True})
        logger.info(f"✅ Captcha passed: {user_id}")

        await message.answer(
            "✅ <b>Tekshiruv muvaffaqiyatli o'tdi!</b>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
        )

        from bot.handlers.user.start import cmd_start
        await cmd_start(message, state)

    else:
        logger.warning(f"❌ Captcha failed: {user_id}, data={message.web_app_data.data}")
        await message.answer(
            "❌ Tekshiruv xato! Qaytadan urinib ko'ring.",
            reply_markup=get_captcha_keyboard(settings.captcha_web_app_url),
        )


__all__ = ["router", "check_captcha"]