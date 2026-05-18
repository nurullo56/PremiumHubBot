# bot/handlers/registration/gender.py
"""
Gender (jins) tanlash
✅ YANGI STRUKTURAGA MOS
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.database.repositories.user_repo import user_repo
from bot.keyboards.user.gender import get_gender_keyboard
from bot.states.user.registration import RegistrationStates

logger = logging.getLogger(__name__)
router = Router(name="registration_gender")


async def check_gender(user_id: int, message: Message) -> bool:
    """
    Gender tekshirish
    
    Returns:
        True - gender tanlangan, davom etish
        False - gender kerak, to'xtatish
    """
    logger.info(f"👤 Gender tekshiruvi...")
    
    user = await user_repo.get_by_id(user_id)
    
    if not user or not user.get("gender"):
        logger.info(f"⏳ Gender kerak: {user_id}")
        await message.answer(
            "👋 Iltimos, jinsingizni tanlang:", 
            reply_markup=get_gender_keyboard()
        )
        return False
    
    logger.info(f"✅ Gender: {user.get('gender')}")
    return True


@router.callback_query(F.data.startswith("gender_"))
async def handle_gender(callback: CallbackQuery, state: FSMContext):
    """Jinsni tanlash"""
    user_id = callback.from_user.id
    gender = "male" if callback.data == "gender_male" else "female"
    
    # Gender saqlash
    await user_repo.update(user_id, {'gender': gender})
    await callback.message.delete()
    await callback.answer("✅ Saqlandi!")
    
    logger.info(f"✅ Gender saved: {user_id} -> {gender}")
    
    # Keyingi bosqich: obuna tekshirish
    from bot.handlers.registration.subscription import ask_subscription
    await ask_subscription(callback.message, state)


__all__ = ["router", "check_gender", "handle_gender"]