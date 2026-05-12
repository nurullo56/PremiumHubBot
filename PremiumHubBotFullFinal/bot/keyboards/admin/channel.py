"""Admin channel management keyboards."""

from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_channel_list_keyboard(channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Channel list management keyboard."""
    keyboard = []
    
    for channel in channels:
        channel_id = channel.get('channel_id', '')
        channel_name = channel.get('channel_name', 'Channel')
        is_active = channel.get('is_active', 1)
        
        status = "✅" if is_active else "⏸️"
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"{status} {channel_name}",
                callback_data=f"channel_info:{channel_id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_channel_actions_keyboard(channel_id: str, is_active: bool) -> InlineKeyboardMarkup:
    """Single channel actions keyboard."""
    toggle_text = "⏸️ To'xtatish" if is_active else "✅ Faollashtirish"
    toggle_callback = f"channel_deactivate:{channel_id}" if is_active else f"channel_activate:{channel_id}"
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=toggle_text, callback_data=toggle_callback)],
            [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"channel_delete:{channel_id}")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="channel_list")]
        ]
    )
