# bot/handlers/admin/broadcast.py
"""Admin broadcast handlers."""

import logging
import asyncio
from aiogram import Router, F, Bot
from bot.filters import IsAdmin
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.admin.broadcast_service import broadcast_service
from bot.states.admin.broadcast import BroadcastStates
from bot.keyboards.admin.broadcast import get_broadcast_target_keyboard, get_broadcast_confirm_keyboard
from bot.keyboards.admin.menu import get_cancel_keyboard, get_admin_main_keyboard
from bot.texts.admin.messages import (
    BROADCAST_START,
    BROADCAST_TARGET,
    BROADCAST_CONFIRM,
    BROADCAST_COMPLETE,
    ADMIN_MENU
)

logger = logging.getLogger(__name__)
router = Router(name="admin_broadcast")


# ==================== HELPER FUNCTIONS ====================

async def cancel_and_return_to_admin(message: Message, state: FSMContext):
    """
    Cancel current operation and return to admin menu.
    This function is used by all cancel handlers.
    """
    # Clear FSM state
    await state.clear()
    
    # Send cancel message
    cancel_msg = await message.answer("❌ Bekor qilindi!")
    
    # Delete the cancel message after 2 seconds
    await asyncio.sleep(2)
    await cancel_msg.delete()
    
    # Show admin main menu
    await message.answer(
        ADMIN_MENU,
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )


async def cancel_callback_and_return_to_admin(callback: CallbackQuery, state: FSMContext):
    """
    Cancel current operation via callback and return to admin menu.
    """
    # Clear FSM state
    await state.clear()
    
    # Edit the callback message to show cancel
    await callback.message.edit_text("❌ Bekor qilindi!")
    
    # Wait a bit
    await asyncio.sleep(1)
    
    # Delete the callback message
    await callback.message.delete()
    
    # Send new admin menu message
    await callback.message.answer(
        ADMIN_MENU,
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )
    
    # Answer callback to remove loading state
    await callback.answer()


# ==================== MAIN HANDLERS ====================

@router.message(IsAdmin(), F.text == "📩 Xabar yuborish")
async def start_broadcast(message: Message, state: FSMContext):
    """
    Start broadcast flow.
    User sends /admin or clicks menu, then this handler starts.
    """
    await message.answer(
        BROADCAST_START,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BroadcastStates.waiting_for_message)


@router.message(BroadcastStates.waiting_for_message, F.text == "❌ Bekor qilish")
async def cancel_broadcast(message: Message, state: FSMContext):
    """
    Cancel broadcast from message state.
    User clicks "Bekor qilish" button while waiting for message.
    """
    await cancel_and_return_to_admin(message, state)


@router.message(BroadcastStates.waiting_for_message, F.text)
async def receive_broadcast_message(message: Message, state: FSMContext):
    """
    Receive the broadcast message text from admin.
    """
    # Save the message text to state
    await state.update_data(message_text=message.text)
    
    # Ask for target selection
    await message.answer(
        BROADCAST_TARGET,
        reply_markup=get_broadcast_target_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BroadcastStates.waiting_for_target)


@router.callback_query(BroadcastStates.waiting_for_target, F.data == "broadcast_cancel")
async def cancel_broadcast_callback(callback: CallbackQuery, state: FSMContext):
    """
    Cancel broadcast from callback state.
    User clicks cancel button in inline keyboard.
    """
    await cancel_callback_and_return_to_admin(callback, state)


@router.callback_query(BroadcastStates.waiting_for_target, F.data.startswith("broadcast_"))
async def select_broadcast_target(callback: CallbackQuery, state: FSMContext):
    """
    Select broadcast target (all users or premium users).
    """
    # Get saved message text from state
    data = await state.get_data()
    message_text = data.get('message_text')
    
    # Determine target
    if callback.data == "broadcast_all":
        target = "all"
    else:
        target = "premium"
    
    # Save target to state
    await state.update_data(target=target)
    
    # Get user count based on target
    from bot.database.repositories.user_repo import user_repo
    
    if target == "all":
        count = await user_repo.get_total_count()
    else:
        from bot.services.premium.premium_service import premium_service
        count = await premium_service.get_active_count()
    
    # Format confirmation message
    text = BROADCAST_CONFIRM.format(
        message=message_text,
        count=count
    )
    
    # Edit the callback message
    await callback.message.edit_text(
        text,
        reply_markup=get_broadcast_confirm_keyboard(),
        parse_mode="HTML"
    )
    
    await callback.answer()


@router.callback_query(IsAdmin(), F.data == "broadcast_confirm")
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Execute the broadcast after confirmation.
    """
    # Get data from state
    data = await state.get_data()
    message_text = data.get('message_text')
    target = data.get('target')
    
    # Show sending status
    await callback.message.edit_text("📤 Yuborilmoqda...")
    
    # Send broadcast based on target
    try:
        if target == "all":
            stats = await broadcast_service.send_broadcast(bot, message_text)
        else:
            stats = await broadcast_service.send_to_premium_users(bot, message_text)
        
        # Format completion message
        text = BROADCAST_COMPLETE.format(
            sent=stats['sent'],
            failed=stats['failed'],
            blocked=stats['blocked']
        )
        
        await callback.message.edit_text(text, parse_mode="HTML")
        
        # Wait a bit before showing admin menu
        await asyncio.sleep(2)
        
        # Show admin menu
        await callback.message.answer(
            ADMIN_MENU,
            reply_markup=get_admin_main_keyboard(),
            parse_mode="HTML"
        )
        
        # Clear state
        await state.clear()
        
    except Exception as e:
        logger.error(f"Broadcast failed: {e}")
        await callback.message.edit_text(
            f"❌ Xatolik yuz berdi: {str(e)}",
            parse_mode="HTML"
        )
        await asyncio.sleep(2)
        await callback.message.answer(
            ADMIN_MENU,
            reply_markup=get_admin_main_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()
    
    await callback.answer()