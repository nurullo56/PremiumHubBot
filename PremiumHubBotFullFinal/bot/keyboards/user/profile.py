"""Profile inline keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Main profile keyboard with spending option."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💰 Balans", callback_data="profile_balance"),
                InlineKeyboardButton(text="👥 Referrallar", callback_data="profile_referrals")
            ],
            [
                InlineKeyboardButton(text="💎 Sarflash", callback_data="spend_menu")
            ]
        ]
    )


def get_balance_keyboard() -> InlineKeyboardMarkup:
    """Balance details keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_profile")]
        ]
    )


def get_referral_keyboard(bot_username: str, user_id: int) -> InlineKeyboardMarkup:
    """Referral keyboard with share button."""
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Ulashish",
                    switch_inline_query=f"Menga qo'shiling! {referral_link}"
                )
            ],
            [
                InlineKeyboardButton(text="👥 Mening referrallarim", callback_data="my_referrals")
            ],
            [
                InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_profile")
            ]
        ]
    )