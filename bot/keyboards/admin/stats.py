from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_stats_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 O'sish", callback_data="stats_growth"),
            InlineKeyboardButton(text="🔍 Batafsil", callback_data="stats_detailed")
        ],
        [
            InlineKeyboardButton(text="📄 Eksport", callback_data="stats_export"),
            InlineKeyboardButton(text="🔄 Yangilash", callback_data="stats_refresh")
        ],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")]
    ])

def get_detailed_stats_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Umumiy", callback_data="stats_overview"),
            InlineKeyboardButton(text="📈 O'sish", callback_data="stats_growth")
        ],
        [
            InlineKeyboardButton(text="📄 Eksport", callback_data="stats_export"),
            InlineKeyboardButton(text="🔄 Yangilash", callback_data="stats_refresh")
        ],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="stats_back")]
    ])
