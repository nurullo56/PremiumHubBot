# bot/keyboards/user/subscription.py
"""Subscription keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def get_subscription_keyboard(channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """
    Get subscription keyboard with channel list.
    
    Args:
        channels: List of channel dicts with channel_id, channel_name, channel_url
    
    Returns:
        InlineKeyboardMarkup: Keyboard with channel buttons and check button
    """
    keyboard = []
    
    # Channel buttons
    for channel in channels:
        channel_url = channel.get('channel_url', '')
        channel_name = channel.get('channel_name', 'Kanal')
        
        if channel_url:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"📢 {channel_name}",
                    url=channel_url
                )
            ])
        else:
            # If no URL, show channel ID
            keyboard.append([
                InlineKeyboardButton(
                    text=f"📢 {channel_name}",
                    callback_data=f"channel_{channel.get('channel_id')}"
                )
            ])
    
    # Check button
    keyboard.append([
        InlineKeyboardButton(
            text="✅ Tekshirish",
            callback_data="check_subscription"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ✅ QO'SHILDI - xatolikni tuzatish uchun
def get_subscription_check_keyboard() -> InlineKeyboardMarkup:
    """
    Get simple subscription check keyboard.
    
    Returns:
        InlineKeyboardMarkup: Keyboard with only check button
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tekshirish",
                    callback_data="check_subscription"
                )
            ]
        ]
    )


def get_subscription_back_keyboard() -> InlineKeyboardMarkup:
    """
    Get back button for subscription.
    
    Returns:
        InlineKeyboardMarkup: Keyboard with back button
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ Orqaga",
                    callback_data="back_to_subscription"
                )
            ]
        ]
    )


__all__ = [
    "get_subscription_keyboard",
    "get_subscription_check_keyboard",  # ✅ EKSPORT QILINDI
    "get_subscription_back_keyboard"
]