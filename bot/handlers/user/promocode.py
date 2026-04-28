"""Promocode handlers."""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.promo.promocode_service import promocode_service
from bot.states.user.promocode import UserPromocodeStates
from bot.texts.user.messages import PROMOCODE_INPUT, PROMOCODE_SUCCESS

logger = logging.getLogger(__name__)
router = Router(name="promocode")


@router.callback_query(F.data == "profile_promocode")
async def ask_promocode(callback: CallbackQuery, state: FSMContext):
    """Ask user to enter promocode."""
    await callback.message.edit_text(PROMOCODE_INPUT)
    await state.set_state(UserPromocodeStates.waiting_for_code)
    await callback.answer()


@router.message(UserPromocodeStates.waiting_for_code, F.text)
async def handle_promocode_input(message: Message, state: FSMContext):
    """Handle promocode input."""
    user_id = message.from_user.id
    code = message.text.strip().upper()
    
    # Validate promocode
    is_valid, error_msg, promo = await promocode_service.validate_promocode(code)
    
    if not is_valid:
        await message.answer(f"❌ {error_msg}")
        return
    
    # Use promocode
    success, msg = await promocode_service.use_promocode(code, user_id)
    
    if success:
        logger.info(f"✅ Promocode used: {code} by {user_id}")
        
        text = PROMOCODE_SUCCESS.format(
            product_name=promo.get('product_name', 'N/A'),
            product_price=promo.get('product_price', 0)
        )
        
        await message.answer(text, parse_mode="HTML")
        
        # Notify promocode owner
        owner_id = promo.get('user_id')
        if owner_id:
            try:
                await message.bot.send_message(
                    owner_id,
                    f"🎉 <b>PROMOKOD ISHLATILDI!</b>\n\n"
                    f"🎟 Kod: {code}\n"
                    f"👤 Foydalanuvchi: {message.from_user.full_name}\n"
                    f"🆔 ID: {user_id}",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to notify owner {owner_id}: {e}")
    else:
        await message.answer(f"❌ {msg}")
    
    await state.clear()
