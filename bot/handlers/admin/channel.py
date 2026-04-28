# bot/handlers/admin/channel.py
"""Admin channel management handlers."""

import logging
import asyncio
from aiogram import Router, F
from bot.filters import IsAdmin
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.channel.channel_service import channel_service
from bot.states.admin.channel import ChannelStates
from bot.keyboards.admin.channel import get_channel_list_keyboard, get_channel_actions_keyboard
from bot.keyboards.admin.menu import get_cancel_keyboard, get_admin_main_keyboard
from bot.texts.admin.messages import (
    CHANNEL_LIST,
    CHANNEL_ADD_PROMPT,
    CHANNEL_ADDED,
    CHANNEL_REMOVED,
    CHANNEL_ACTIVATED,
    CHANNEL_DEACTIVATED,
    ADMIN_MENU
)

logger = logging.getLogger(__name__)
router = Router(name="admin_channel")


# ==================== HELPER FUNCTIONS ====================

async def cancel_and_return_to_admin(message: Message, state: FSMContext):
    """Cancel current operation and return to admin menu."""
    await state.clear()
    
    cancel_msg = await message.answer("❌ Bekor qilindi!")
    await asyncio.sleep(2)
    await cancel_msg.delete()
    
    await message.answer(
        ADMIN_MENU,
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )


# ==================== MAIN HANDLERS ====================

@router.message(IsAdmin(), F.text == "📃 Kanal ro'yxati")
async def show_channel_list(message: Message):
    """Show list of all channels."""
    channels = await channel_service.get_all_channels()
    
    if not channels:
        await message.answer("📢 Hech qanday kanal topilmadi.")
        return
    
    # Format channels list
    channels_text = ""
    for idx, ch in enumerate(channels, 1):
        status = "✅" if ch.get('is_active') else "⏸️"
        channels_text += f"{idx}. {status} {ch.get('channel_name')}\n"
    
    text = CHANNEL_LIST.format(
        channels=channels_text,
        count=len(channels)
    )
    
    await message.answer(
        text,
        reply_markup=get_channel_list_keyboard(channels),
        parse_mode="HTML"
    )


@router.message(IsAdmin(), F.text == "➕ Kanal qo'shish")
async def add_channel_start(message: Message, state: FSMContext):
    """Start the channel adding flow."""
    await message.answer(
        CHANNEL_ADD_PROMPT,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ChannelStates.waiting_for_channel_input)


@router.message(ChannelStates.waiting_for_channel_input, F.text == "❌ Bekor qilish")
async def cancel_add_channel(message: Message, state: FSMContext):
    """Cancel adding channel."""
    await cancel_and_return_to_admin(message, state)


@router.message(ChannelStates.waiting_for_channel_input, F.text)
async def receive_channel_data(message: Message, state: FSMContext):
    """
    Receive and parse channel data.
    Format: channel_id | channel_name | channel_url
    """
    try:
        # Parse input: channel_id | channel_name | channel_url
        parts = [p.strip() for p in message.text.split('|')]
        
        if len(parts) < 3:
            await message.answer(
                "❌ Noto'g'ri format!\n\n"
                "To'g'ri format:\n"
                "<code>-100123456789 | Mening Kanalim | https://t.me/my_channel</code>",
                parse_mode="HTML"
            )
            return
        
        channel_id = parts[0]
        channel_name = parts[1]
        channel_url = parts[2]
        
        # Add channel using service
        success = await channel_service.add_channel(
            channel_id=channel_id,
            channel_name=channel_name,
            channel_url=channel_url,
            added_by=message.from_user.id
        )
        
        if success:
            logger.info(f"✅ Channel added: {channel_id} by {message.from_user.id}")
            
            # Show success message
            await message.answer(CHANNEL_ADDED)
            
            # Clear state
            await state.clear()
            
            # Show admin menu after a moment
            await asyncio.sleep(1.5)
            await message.answer(
                ADMIN_MENU,
                reply_markup=get_admin_main_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Kanal qo'shishda xatolik yuz berdi!")
            
    except Exception as e:
        logger.error(f"Error adding channel: {e}")
        await message.answer("❌ Xatolik yuz berdi! Iltimos, qaytadan urinib ko'ring.")


@router.callback_query(F.data.startswith("channel_activate:"))
async def activate_channel(callback: CallbackQuery):
    """Activate a channel."""
    channel_id = callback.data.split(':')[1]
    
    success = await channel_service.activate_channel(channel_id)
    
    if success:
        await callback.answer(CHANNEL_ACTIVATED, show_alert=True)
        # Refresh the channel list
        await show_channel_list(callback.message)
    else:
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("channel_deactivate:"))
async def deactivate_channel(callback: CallbackQuery):
    """Deactivate a channel."""
    channel_id = callback.data.split(':')[1]
    
    success = await channel_service.deactivate_channel(channel_id)
    
    if success:
        await callback.answer(CHANNEL_DEACTIVATED, show_alert=True)
        # Refresh the channel list
        await show_channel_list(callback.message)
    else:
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("channel_delete:"))
async def delete_channel(callback: CallbackQuery):
    """Delete a channel permanently."""
    channel_id = callback.data.split(':')[1]
    
    # Ask for confirmation
    success = await channel_service.remove_channel(channel_id)
    
    if success:
        await callback.answer(CHANNEL_REMOVED, show_alert=True)
        # Refresh the channel list
        await show_channel_list(callback.message)
    else:
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)
    
    await callback.answer()