# bot/handlers/registration/phone.py
"""
Telefon raqam qabul qilish va validatsiya
✅ YANGI STRUKTURAGA MOS
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.database.repositories.user_repo import user_repo
from bot.database.repositories.balance_repo import balance_repo
from bot.keyboards.user.main_menu import get_phone_keyboard, get_main_keyboard
from bot.states.user.registration import RegistrationStates
from bot.utils.validators.phone_validator import validate_phone, normalize_phone

logger = logging.getLogger(__name__)
router = Router(name="registration_phone")


async def check_phone(user_id: int, message: Message) -> bool:
    """
    Telefon tekshirish
    
    Returns:
        True - telefon bor, davom etish
        False - telefon kerak, to'xtatish
    """
    logger.info(f"📱 Telefon tekshiruvi...")
    
    user = await user_repo.get_by_id(user_id)
    phone = user.get('phone') if user else None
    
    if not phone:
        logger.info(f"⏳ Telefon kerak: {user_id}")
        await message.answer(
            "📱 <b>Telefon raqamingiz kerak</b>\n\n"
            "Botdan foydalanish uchun telefon raqamingizni yuboring:",
            reply_markup=get_phone_keyboard(),
            parse_mode="HTML"
        )
        return False
    
    logger.info(f"✅ Telefon: {phone}")
    return True


async def ask_phone(message: Message, state: FSMContext):
    """Telefon raqam so'rash"""
    await message.answer(
        "📱 <b>Telefon raqamingiz kerak</b>\n\n"
        "Botdan foydalanish uchun telefon raqamingizni yuboring:",
        reply_markup=get_phone_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def handle_contact_phone(message: Message, state: FSMContext):
    """Telefon raqam qabul qilish (contact tugma orqali)"""
    user_id = message.from_user.id
    phone = message.contact.phone_number
    
    normalized = normalize_phone(phone)
    
    # Multi-akkaunt tekshiruvi
    phone_exists, existing_user_id = await user_repo.phone_exists(normalized)
    
    if phone_exists and existing_user_id != user_id:
        logger.warning(f"🚫 MULTI-AKKAUNT! Telefon: {normalized}, Mavjud: {existing_user_id}, Yangi: {user_id}")
        await message.answer(
            "🚫 <b>Xatolik!</b>\n\n"
            f"Bu telefon raqami (<code>{normalized}</code>) allaqachon "
            f"boshqa akkaunt tomonidan ishlatilgan.\n\n"
            f"📱 Bir telefon raqamidan faqat <b>bitta akkaunt</b> yaratish mumkin.",
            parse_mode="HTML"
        )
        return
    
    await user_repo.update(user_id, {'phone': normalized, 'last_phone_update': None})
    logger.info(f"✅ Telefon saqlandi: {user_id} -> {normalized}")
    
    await message.answer("✅ Telefon raqami saqlandi!")
    await state.clear()
    
    # Keyingi bosqich: subscription yoki main menu
    from bot.handlers.registration.subscription import check_subscription
    from bot.services.channel.channel_service import channel_service
    
    channels = await channel_service.get_active_channels()
    
    if channels:
        # Kanallar bor — subscription check
        await check_subscription(user_id, message, message.bot)
    else:
        # Kanallar yo'q — to'g'ridan-to'g'ri main menu
        await user_repo.update_subscription(user_id, True)
        balance = await balance_repo.get_balance(user_id)
        fullname = message.from_user.full_name
        
        await message.answer(
            f"✅ <b>Ro'yxatdan o'tish tugallandi!</b>\n\n"
            f"👋 Xush kelibsiz, {fullname}!\n"
            f"💰 Balansingiz: {float(balance):.2f} 💎\n\n"
            f"🎁 <b>Bonus olish uchun:</b>\n"
            f"\"✨BEPUL PREMIUM OLISH💫\" tugmasini bosing!",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )


@router.message(RegistrationStates.waiting_for_phone, F.text)
async def handle_text_phone(message: Message, state: FSMContext):
    """Telefon raqam qabul qilish (matn orqali)"""
    user_id = message.from_user.id
    phone = message.text.strip()
    
    is_valid, error_msg = validate_phone(phone)
    
    if not is_valid:
        await message.answer(f"❌ {error_msg}\n\nQaytadan kiriting:")
        return
    
    normalized = normalize_phone(phone)
    
    # Multi-akkaunt tekshiruvi
    phone_exists, existing_user_id = await user_repo.phone_exists(normalized)
    
    if phone_exists and existing_user_id != user_id:
        logger.warning(f"🚫 MULTI-AKKAUNT! Telefon: {normalized}")
        await message.answer(
            "🚫 <b>Xatolik!</b>\n\n"
            f"Bu telefon raqami (<code>{normalized}</code>) allaqachon "
            f"boshqa akkaunt tomonidan ishlatilgan.\n\n"
            f"📱 Bir telefon raqamidan faqat <b>bitta akkaunt</b> yaratish mumkin.",
            parse_mode="HTML"
        )
        return
    
    await user_repo.update(user_id, {'phone': normalized, 'last_phone_update': None})
    logger.info(f"✅ Telefon saqlandi: {user_id} -> {normalized}")
    
    await message.answer("✅ Telefon raqami saqlandi!")
    await state.clear()
    
    # Keyingi bosqich: subscription yoki main menu
    from bot.handlers.registration.subscription import check_subscription
    from bot.services.channel.channel_service import channel_service
    
    channels = await channel_service.get_active_channels()
    
    if channels:
        # Kanallar bor — subscription check
        await check_subscription(user_id, message, message.bot)
    else:
        # Kanallar yo'q — to'g'ridan-to'g'ri main menu
        await user_repo.update_subscription(user_id, True)
        balance = await balance_repo.get_balance(user_id)
        fullname = message.from_user.full_name
        
        await message.answer(
            f"✅ <b>Ro'yxatdan o'tish tugallandi!</b>\n\n"
            f"👋 Xush kelibsiz, {fullname}!\n"
            f"💰 Balansingiz: {float(balance):.2f} 💎\n\n"
            f"🎁 <b>Bonus olish uchun:</b>\n"
            f"\"✨BEPUL PREMIUM OLISH💫\" tugmasini bosing!",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )


__all__ = ["router", "check_phone", "ask_phone", "handle_contact_phone", "handle_text_phone"]