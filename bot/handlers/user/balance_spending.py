"""Balance spending and product purchase handlers."""

import logging
import random
import string
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from bot.database.repositories.user_repo import user_repo
from bot.services.finance.balance_service import balance_service
from bot.services.referral.referral_service import referral_service
from bot.config import settings
from bot.config.constants import TRANSACTION_PURCHASE

logger = logging.getLogger(__name__)
router = Router(name="spending")


# ==================== PRODUCTS CONFIGURATION ====================

PROMOCODE_PREFIXES = {
    "premium": "PREM",
    "teddy": "TEDY",
    "heart": "HART",
    "rose": "ROSE",
    "gift": "GIFT",
    "bottle": "BOTL",
    "cake": "CAKE",
    "trophy": "TRPY",
    "ring": "RING",
    "stars": "STAR",
    "tree": "TREE"
}

PRODUCTS = {
    "premium": {"name": "⭐️ Telegram Premium", "price": 55, "type": "premium"},
    "teddy": {"name": "50 🧸 Ayiqcha", "price": 27, "type": "teddy"},
    "heart": {"name": "15 💝 Yurak", "price": 12, "type": "heart"},
    "rose": {"name": "25 🌹 Atirgul", "price": 20, "type": "rose"},
    "gift": {"name": "25 🎁 Sovg'a", "price": 20, "type": "gift"},
    "bottle": {"name": "50 🍾 Shampan", "price": 27, "type": "bottle"},
    "cake": {"name": "50 🎂 Tort", "price": 27, "type": "cake"},
    "trophy": {"name": "100 🏆 Kubok", "price": 29, "type": "trophy"},
    "ring": {"name": "100 💍 Uzuk", "price": 39, "type": "ring"},
    "stars": {"name": "100 💎 Stars", "price": 39, "type": "stars"},
    "tree": {"name": "50 🎄 Archa", "price": 27, "type": "tree"}
}


# ==================== HELPER FUNCTIONS ====================

def generate_promocode(user_id: int, product_type: str) -> str:
    """Generate unique promocode."""
    prefix = PROMOCODE_PREFIXES.get(product_type, "PROMO")
    random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{prefix}-{user_id}-{random_code}"


def get_spend_products_keyboard():
    """Get products keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="⭐️ Premium - 55💎", callback_data="buy_premium_55")],
        [
            InlineKeyboardButton(text="🧸 Ayiqcha - 27💎", callback_data="buy_teddy_27"),
            InlineKeyboardButton(text="💝 Yurak - 12💎", callback_data="buy_heart_12")
        ],
        [
            InlineKeyboardButton(text="🌹 Atirgul - 20💎", callback_data="buy_rose_20"),
            InlineKeyboardButton(text="🎁 Sovg'a - 20💎", callback_data="buy_gift_20")
        ],
        [
            InlineKeyboardButton(text="🍾 Shampan - 27💎", callback_data="buy_bottle_27"),
            InlineKeyboardButton(text="🎂 Tort - 27💎", callback_data="buy_cake_27")
        ],
        [
            InlineKeyboardButton(text="🏆 Kubok - 29💎", callback_data="buy_trophy_29"),
            InlineKeyboardButton(text="💍 Uzuk - 39💎", callback_data="buy_ring_39")
        ],
        [
            InlineKeyboardButton(text="💎 Stars - 39💎", callback_data="buy_stars_39"),
            InlineKeyboardButton(text="🎄 Archa - 27💎", callback_data="buy_tree_27")
        ],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_profile")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_purchase_success_keyboard():
    """Keyboard after successful purchase."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Admin", url=f"https://t.me/{settings.admin_username.lstrip('@')}")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_profile")]
    ])


def get_insufficient_balance_keyboard():
    """Keyboard when balance is insufficient."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Do'stlarni taklif qiling", callback_data="profile_referrals")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_profile")]
    ])


async def notify_admin_purchase(
    bot,
    user: dict,
    product_name: str,
    price: int,
    promocode: str,
    referral_count: int,
    new_balance: float
) -> bool:
    """Notify admin about purchase."""
    try:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        user_id = user['user_id']
        fullname = user['fullname']
        username = user.get('username', 'username_yoq')
        
        text = f"""
🛒 <b>YANGI XARID!</b>

━━━━━━━━━━━━━━━━━━━━
👤 <b>Foydalanuvchi:</b>
• Ism: {fullname}
• Username: @{username}
• ID: <code>{user_id}</code>

━━━━━━━━━━━━━━━━━━━━
📦 <b>Mahsulot:</b> {product_name}
💎 <b>Narx:</b> {price} olmos
💰 <b>Yangi balans:</b> {new_balance:.2f} 💎

━━━━━━━━━━━━━━━━━━━━
🎟 <b>PROMOKOD:</b>
<code>{promocode}</code>

━━━━━━━━━━━━━━━━━━━━
📊 <b>Statistika:</b>
• Referallar: {referral_count}
"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 Referrallar", callback_data=f"admin_view_refs:{user_id}")]
        ])
        
        await bot.send_message(
            settings.first_admin_id,
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        logger.info(f"✅ Admin notified: {user_id} - {product_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Admin notification failed: {e}")
        return False


# ==================== HANDLERS ====================

@router.callback_query(F.data == "spend_menu")
async def spend_menu_callback(callback: CallbackQuery):
    """Show spending menu."""
    text = """
💎 <b>Olmoslaringizni sarflang!</b>

Yig'ilgan olmoslaringizni o'zingiz xohlagan narsalarga almashtirib olishingiz mumkin!

Quyidagilarni ko'rib va ulardan unumli foydalaning. 👇
"""
    
    keyboard = get_spend_products_keyboard()
    
    if settings.spend_image_id:
        await callback.message.answer_photo(
            photo=settings.spend_image_id,
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.message.delete()
    else:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    await callback.answer()


async def buy_product(callback: CallbackQuery, product_key: str):
    """Process product purchase."""
    try:
        user_id = callback.from_user.id
        
        product = PRODUCTS.get(product_key)
        if not product:
            await callback.answer("❌ Mahsulot topilmadi!", show_alert=True)
            return
        
        product_name = product["name"]
        price = product["price"]
        product_type = product["type"]
        
        # Get user data
        user = await user_repo.get_by_id(user_id)
        if not user:
            await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
            return
        
        # Check balance
        balance = await balance_service.get_balance(user_id)
        
        if balance >= price:
            # Generate promocode
            promocode = generate_promocode(user_id, product_type)
            
            # Deduct balance
            success, _, _ = await balance_service.subtract_balance(
                user_id,
                price,
                f"Xarid: {product_name} (Promokod: {promocode})",
                TRANSACTION_PURCHASE
            )
            
            if success:
                # Get new balance
                new_balance = await balance_service.get_balance(user_id)
                
                # Notify admin
                referral_count = await referral_service.get_referral_count(user_id)
                await notify_admin_purchase(
                    callback.bot,
                    user,
                    product_name,
                    price,
                    promocode,
                    referral_count,
                    new_balance
                )
                
                # User success message
                text = f"""
🎉 <b>Xarid muvaffaqiyatli!</b>

📦 <b>Mahsulot:</b> {product_name}
💎 <b>Narx:</b> {price} olmos
💰 <b>Yangi balans:</b> {new_balance:.2f} 💎

━━━━━━━━━━━━━━━━━━━━
🎟 <b>SIZNING PROMOKODINGIZ:</b>

<code>{promocode}</code>

━━━━━━━━━━━━━━━━━━━━

📝 <b>Qanday foydalanish:</b>
1️⃣ Admin bilan bog'laning: @{settings.admin_username.lstrip('@')}
2️⃣ Promokodni yuboring
3️⃣ Mahsulotni oling!

⏰ <b>Promokod amal qilish muddati:</b> 24 soat

<i>💡 Promokodni nusxalang va adminga yuboring!</i>
"""
                
                keyboard = get_purchase_success_keyboard()
                
                try:
                    await callback.message.edit_caption(
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                except:
                    await callback.message.edit_text(
                        text=text,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                
                logger.info(f"✅ Purchase successful: {user_id} -> {product_name} ({price}💎)")
            else:
                await callback.answer("❌ Balansni kamaytirishda xatolik!", show_alert=True)
        
        else:
            # Insufficient balance
            shortage = price - balance
            
            text = f"""
❌ <b>Balansingiz yetarli emas!</b>

📦 <b>Mahsulot:</b> {product_name}
💎 <b>Narx:</b> {price} olmos
💰 <b>Sizning balansingiz:</b> {balance:.2f} 💎
📉 <b>Yetmayotgan:</b> {shortage:.2f} 💎

<i>💡 Referal tizimi orqali ko'proq olmos to'plang!</i>
"""
            
            keyboard = get_insufficient_balance_keyboard()
            
            try:
                await callback.message.edit_caption(
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            except:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ Purchase error: {e}", exc_info=True)
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)


# ==================== PRODUCT HANDLERS ====================

@router.callback_query(F.data == "buy_premium_55")
async def buy_premium_handler(callback: CallbackQuery):
    await buy_product(callback, "premium")


@router.callback_query(F.data == "buy_teddy_27")
async def buy_teddy_handler(callback: CallbackQuery):
    await buy_product(callback, "teddy")


@router.callback_query(F.data == "buy_heart_12")
async def buy_heart_handler(callback: CallbackQuery):
    await buy_product(callback, "heart")


@router.callback_query(F.data == "buy_rose_20")
async def buy_rose_handler(callback: CallbackQuery):
    await buy_product(callback, "rose")


@router.callback_query(F.data == "buy_gift_20")
async def buy_gift_handler(callback: CallbackQuery):
    await buy_product(callback, "gift")


@router.callback_query(F.data == "buy_bottle_27")
async def buy_bottle_handler(callback: CallbackQuery):
    await buy_product(callback, "bottle")


@router.callback_query(F.data == "buy_cake_27")
async def buy_cake_handler(callback: CallbackQuery):
    await buy_product(callback, "cake")


@router.callback_query(F.data == "buy_trophy_29")
async def buy_trophy_handler(callback: CallbackQuery):
    await buy_product(callback, "trophy")


@router.callback_query(F.data == "buy_ring_39")
async def buy_ring_handler(callback: CallbackQuery):
    await buy_product(callback, "ring")


@router.callback_query(F.data == "buy_stars_39")
async def buy_stars_handler(callback: CallbackQuery):
    await buy_product(callback, "stars")


@router.callback_query(F.data == "buy_tree_27")
async def buy_tree_handler(callback: CallbackQuery):
    await buy_product(callback, "tree")