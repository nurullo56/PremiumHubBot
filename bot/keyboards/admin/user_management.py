"""User management inline keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_user_management_keyboard(user_id: int, is_blocked: bool) -> InlineKeyboardMarkup:
    """Get user management actions keyboard."""
    block_text = "✅ Blokdan chiqarish" if is_blocked else "🚫 Bloklash"
    block_action = "unblock" if is_blocked else "block"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=block_text,
                callback_data=f"user_{block_action}:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="💰 Balans qo'shish",
                callback_data=f"user_add_balance:{user_id}"
            ),
            InlineKeyboardButton(
                text="💸 Balans ayirish",
                callback_data=f"user_subtract_balance:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⭐ Premium berish",
                callback_data=f"user_give_premium:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="admin_back"
            )
        ]
    ])


def get_premium_requests_keyboard(requests: list) -> InlineKeyboardMarkup:
    """Get premium requests list keyboard."""
    buttons = []
    
    for req in requests[:10]:  # Max 10
        user_id = req.get('user_id')
        fullname = req.get('fullname', 'N/A')
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {fullname} (ID: {user_id})",
                callback_data=f"premium_view:{user_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_premium_action_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Premium request actions."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Tasdiqlash",
                callback_data=f"premium_approve:{user_id}"
            ),
            InlineKeyboardButton(
                text="❌ Rad etish",
                callback_data=f"premium_reject:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="premium_requests"
            )
        ]
    ])
