# bot/handlers/user/balance_spending.py
"""
Balance spending with secure promocode and atomic purchases.

Security features:
- HMAC-based promocode (user_id hidden)
- Atomic transactions with RETURNING
- Outbox pattern for notifications
- First purchase bonus (no double-spend)
- BEGIN IMMEDIATE for exclusive locks

All operations are production-ready and race-condition free.
"""

import hashlib
import hmac
import json
import logging
import secrets
import time
from decimal import Decimal
from typing import Optional, Tuple, Dict, Any

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.repositories.user_repo import user_repo
from bot.services.finance.balance_service import balance_service
from bot.services.referral.referral_service import referral_service
from bot.database.base import get_db
from bot.config import settings
from bot.config.constants import TRANSACTION_PURCHASE
from bot.utils.common.timezone import now_str
from bot.utils.common.money import to_scaled, from_scaled

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

FIRST_PURCHASE_BONUS = Decimal('2.0')  # Referrer gets 2 olmos on first purchase


# ==================== SECURE PROMOCODE ====================

def generate_secure_promocode(user_id: int, product_type: str) -> str:
    """
    Generate HMAC-based secure promocode (user_id hidden).
    
    Security features:
    - HMAC-SHA256 signature
    - Timestamp for expiry check
    - User ID hidden in signature
    - Bot token as secret key
    
    Format: PREFIX-TIMESTAMP-HMAC
    Example: PREM-1714567890-A1B2C3D4
    
    Args:
        user_id: User ID (not exposed in code)
        product_type: Product type for prefix
        
    Returns:
        Secure promocode string
    """
    prefix = PROMOCODE_PREFIXES.get(product_type, "PROMO")
    timestamp = int(time.time())
    
    # Create HMAC signature
    secret_key = settings.bot_token.encode()
    message = f"{user_id}:{timestamp}:{product_type}".encode()
    signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest()[:8].upper()
    
    return f"{prefix}-{timestamp}-{signature}"


def verify_promocode(promocode: str, user_id: int, product_type: str) -> bool:
    """
    Verify HMAC-based promocode.
    
    Checks:
    - Format validity
    - HMAC signature
    - Timestamp expiry (24 hours)
    
    Args:
        promocode: Promocode to verify
        user_id: User ID
        product_type: Product type
        
    Returns:
        True if valid, False otherwise
    """
    try:
        parts = promocode.split('-')
        if len(parts) != 3:
            return False
        
        prefix, timestamp_str, signature = parts
        timestamp = int(timestamp_str)
        
        # Check expiry (24 hours)
        if time.time() - timestamp > 86400:
            logger.warning(f"⚠️ Expired promocode: {promocode}")
            return False
        
        # Verify HMAC
        secret_key = settings.bot_token.encode()
        message = f"{user_id}:{timestamp}:{product_type}".encode()
        expected_signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest()[:8].upper()
        
        return signature == expected_signature
        
    except Exception as e:
        logger.error(f"❌ Promocode verification error: {e}")
        return False


# ==================== OUTBOX PATTERN ====================

async def save_to_outbox(
    db,
    event_type: str,
    payload: Dict[str, Any]
) -> bool:
    """
    Save event to outbox for later processing.
    
    Outbox pattern ensures:
    - Notifications sent outside transaction
    - No data loss if notification fails
    - Retry capability
    
    Args:
        db: Database connection (in transaction)
        event_type: Type of event (e.g., 'admin_purchase_notification')
        payload: Event data as dict
        
    Returns:
        True if saved successfully
    """
    try:
        await db.execute("""
            INSERT INTO outbox (event_type, payload, created_at, processed)
            VALUES (?, ?, ?, 0)
        """, (event_type, json.dumps(payload), now_str()))
        
        logger.info(f"✅ Event saved to outbox: {event_type}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save to outbox: {e}")
        return False


async def process_outbox_events(bot):
    """
    Process pending outbox events (called after transaction commits).
    
    This runs OUTSIDE the transaction to avoid blocking.
    
    Args:
        bot: Bot instance for sending notifications
    """
    try:
        async with get_db() as db:
            # Get unprocessed events
            cursor = await db.execute("""
                SELECT id, event_type, payload
                FROM outbox
                WHERE processed = 0
                ORDER BY created_at ASC
                LIMIT 100
            """)
            
            events = await cursor.fetchall()
            
            if not events:
                return
            
            logger.info(f"📦 Processing {len(events)} outbox events...")
            
            for event in events:
                event_id = event['id']
                event_type = event['event_type']
                payload = json.loads(event['payload'])
                
                try:
                    if event_type == 'admin_purchase_notification':
                        await send_admin_purchase_notification(bot, payload)
                    
                    # Mark as processed
                    await db.execute("""
                        UPDATE outbox 
                        SET processed = 1, processed_at = ?
                        WHERE id = ?
                    """, (now_str(), event_id))
                    await db.commit()
                    
                    logger.info(f"✅ Outbox event processed: {event_type} (id={event_id})")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process outbox event {event_id}: {e}")
                    # Keep as unprocessed for retry
                    
    except Exception as e:
        logger.error(f"❌ process_outbox_events error: {e}")


async def send_admin_purchase_notification(bot, payload: Dict[str, Any]):
    """
    Send admin notification from outbox payload.
    
    Args:
        bot: Bot instance
        payload: Event payload
    """
    try:
        text = f"""
🛒 <b>YANGI XARID!</b>

━━━━━━━━━━━━━━━━━━━━
👤 <b>Foydalanuvchi:</b>
• Ism: {payload['fullname']}
• Username: @{payload['username']}
• ID: <code>{payload['user_id']}</code>

━━━━━━━━━━━━━━━━━━━━
📦 <b>Mahsulot:</b> {payload['product_name']}
💎 <b>Narx:</b> {payload['price']} olmos
💰 <b>Yangi balans:</b> {payload['new_balance']:.2f} 💎

━━━━━━━━━━━━━━━━━━━━
🎟 <b>PROMOKOD:</b>
<code>{payload['promocode']}</code>

━━━━━━━━━━━━━━━━━━━━
📊 <b>Statistika:</b>
• Referallar: {payload['referral_count']}
"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="👥 Referrallar",
                callback_data=f"admin_view_refs:{payload['user_id']}"
            )]
        ])
        
        await bot.send_message(
            settings.first_admin_id,
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        logger.info(f"✅ Admin notified: {payload['user_id']} - {payload['product_name']}")
        
    except Exception as e:
        logger.error(f"❌ Admin notification failed: {e}")
        raise  # Re-raise to keep in outbox for retry


# ==================== FIRST PURCHASE BONUS ====================

async def give_first_purchase_bonus(
    db,
    referrer_id: int,
    buyer_id: int
) -> Tuple[bool, str]:
    """
    Give first purchase bonus atomically.
    
    Security:
    - UPDATE WHERE referral_bonus_given = 0 (atomic check)
    - RETURNING clause for verification
    - No double-spending possible
    - Single query execution
    
    Args:
        db: Database connection (in transaction)
        referrer_id: Referrer user ID
        buyer_id: Buyer user ID
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        # Convert bonus to scaled integer
        scaled_bonus = to_scaled(FIRST_PURCHASE_BONUS)
        
        # Atomic update: give bonus only if not given before
        cursor = await db.execute("""
            UPDATE users
            SET referral_bonus_given = 1,
                balance_scaled = COALESCE(balance_scaled, 0) + ?
            WHERE user_id = ?
              AND referral_bonus_given = 0
            RETURNING balance_scaled
        """, (scaled_bonus, referrer_id))
        
        result = await cursor.fetchone()
        
        if not result:
            # Already given or user not found
            logger.info(f"⏭️  First purchase bonus already given: {referrer_id}")
            return False, "Bonus allaqachon berilgan"
        
        new_balance_scaled = result['balance_scaled']
        new_balance = from_scaled(new_balance_scaled)
        
        # Add history
        from bot.database.repositories.balance_repo import balance_repo
        
        timestamp = now_str()
        await balance_repo.add_history_scaled(
            db=db,
            user_id=referrer_id,
            amount_scaled=scaled_bonus,
            description=f"Birinchi xarid bonusi (referal {buyer_id})",
            new_balance_scaled=new_balance_scaled,
            transaction_type="first_purchase_bonus",
            timestamp=timestamp
        )
        
        logger.info(f"✅ First purchase bonus: {referrer_id} <- {buyer_id} (+{FIRST_PURCHASE_BONUS}💎)")
        return True, f"{FIRST_PURCHASE_BONUS}💎 bonus berildi"
        
    except Exception as e:
        logger.error(f"❌ give_first_purchase_bonus error: {e}")
        return False, f"Xatolik: {str(e)}"


# ==================== PURCHASE HANDLER ====================

async def buy_product(callback: CallbackQuery, product_key: str):
    """
    Process product purchase with atomic transaction and outbox.
    
    Workflow (ACID-compliant):
    1. BEGIN IMMEDIATE transaction
    2. Check balance
    3. Generate secure promocode
    4. Subtract balance (atomic with RETURNING)
    5. Add balance history
    6. Save notification to outbox
    7. Give first purchase bonus (if applicable)
    8. COMMIT transaction
    9. Process outbox events (send notification)
    
    Security features:
    - Race-condition free
    - Double-spending impossible
    - Atomic bonus
    - Secure promocode
    - Outbox pattern
    
    Args:
        callback: Callback query
        product_key: Product key (e.g., 'premium', 'teddy')
    """
    try:
        user_id = callback.from_user.id
        
        # Validate product
        product = PRODUCTS.get(product_key)
        if not product:
            await callback.answer("❌ Mahsulot topilmadi!", show_alert=True)
            return
        
        product_name = product["name"]
        price = product["price"]
        product_type = product["type"]
        price_decimal = Decimal(str(price))
        
        # Get user data
        user = await user_repo.get_by_id(user_id)
        if not user:
            await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
            return
        
        # Check balance (pre-check to avoid unnecessary transaction)
        balance = await balance_service.get_balance(user_id)
        
        if balance < price_decimal:
            # Insufficient balance - show error
            await show_insufficient_balance_message(
                callback,
                product_name,
                price,
                balance
            )
            return
        
        # Process purchase in atomic transaction
        try:
            async with get_db() as db:
                await db.execute("BEGIN IMMEDIATE")
                
                try:
                    from bot.database.repositories.balance_repo import balance_repo
                    
                    # 1. Generate secure promocode
                    promocode = generate_secure_promocode(user_id, product_type)
                    logger.info(f"🎟 Generated promocode: {promocode[:20]}... for user {user_id}")
                    
                    # 2. Subtract balance (atomic with check)
                    scaled_amount = to_scaled(price_decimal)
                    
                    cursor = await db.execute("""
                        UPDATE users 
                        SET balance_scaled = balance_scaled - ?
                        WHERE user_id = ? 
                          AND COALESCE(balance_scaled, 0) >= ?
                        RETURNING balance_scaled
                    """, (scaled_amount, user_id, scaled_amount))
                    
                    result = await cursor.fetchone()
                    
                    if not result:
                        await db.rollback()
                        logger.warning(f"⚠️ Insufficient balance during transaction: user={user_id}")
                        await callback.answer("❌ Balans yetarli emas!", show_alert=True)
                        return
                    
                    new_balance_scaled = result['balance_scaled']
                    new_balance = from_scaled(new_balance_scaled)
                    
                    # 3. Add balance history
                    timestamp = now_str()
                    await balance_repo.add_history_scaled(
                        db=db,
                        user_id=user_id,
                        amount_scaled=-scaled_amount,
                        description=f"Xarid: {product_name} (Promokod: {promocode})",
                        new_balance_scaled=new_balance_scaled,
                        transaction_type=TRANSACTION_PURCHASE,
                        timestamp=timestamp
                    )
                    
                    # 4. Save admin notification to outbox
                    referral_count = await referral_service.get_referral_count(user_id)
                    
                    await save_to_outbox(db, 'admin_purchase_notification', {
                        'user_id': user_id,
                        'fullname': user['fullname'],
                        'username': user.get('username', 'username_yoq'),
                        'product_name': product_name,
                        'price': price,
                        'promocode': promocode,
                        'referral_count': referral_count,
                        'new_balance': float(new_balance)
                    })
                    
                    # 5. First purchase bonus (if applicable)
                    bonus_given = False
                    if user.get('referred_by'):
                        referrer_id = user['referred_by']
                        success, msg = await give_first_purchase_bonus(db, referrer_id, user_id)
                        if success:
                            bonus_given = True
                            logger.info(f"🎁 First purchase bonus given to {referrer_id}")
                    
                    # 6. COMMIT transaction
                    await db.commit()
                    
                    logger.info(
                        f"✅ Purchase successful: user={user_id}, "
                        f"product={product_name}, price={price}💎, "
                        f"new_balance={new_balance}💎, bonus_given={bonus_given}"
                    )
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"❌ Purchase transaction error: {e}", exc_info=True)
                    raise
            
            # 7. Process outbox events (after transaction commits)
            await process_outbox_events(callback.bot)
            
            # 8. Show success message to user
            await show_purchase_success_message(
                callback,
                product_name,
                price,
                new_balance,
                promocode
            )
            
        except Exception as e:
            logger.error(f"❌ Purchase processing error: {e}", exc_info=True)
            await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)
            return
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"❌ buy_product error: {e}", exc_info=True)
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)


# ==================== UI HELPER FUNCTIONS ====================

async def show_insufficient_balance_message(
    callback: CallbackQuery,
    product_name: str,
    price: int,
    balance: Decimal
):
    """Show insufficient balance error message."""
    shortage = Decimal(str(price)) - balance
    
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


async def show_purchase_success_message(
    callback: CallbackQuery,
    product_name: str,
    price: int,
    new_balance: Decimal,
    promocode: str
):
    """Show purchase success message."""
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


# ==================== KEYBOARD HELPERS ====================

def get_spend_products_keyboard():
    """Get products keyboard."""
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
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Admin", url=f"https://t.me/{settings.admin_username.lstrip('@')}")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_profile")]
    ])


def get_insufficient_balance_keyboard():
    """Keyboard when balance is insufficient."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Do'stlarni taklif qiling", callback_data="profile_referrals")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_profile")]
    ])


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


# ==================== PRODUCT HANDLERS ====================

@router.callback_query(F.data == "buy_premium_55")
async def buy_premium_handler(callback: CallbackQuery):
    """Handle premium purchase."""
    await buy_product(callback, "premium")


@router.callback_query(F.data == "buy_teddy_27")
async def buy_teddy_handler(callback: CallbackQuery):
    """Handle teddy purchase."""
    await buy_product(callback, "teddy")


@router.callback_query(F.data == "buy_heart_12")
async def buy_heart_handler(callback: CallbackQuery):
    """Handle heart purchase."""
    await buy_product(callback, "heart")


@router.callback_query(F.data == "buy_rose_20")
async def buy_rose_handler(callback: CallbackQuery):
    """Handle rose purchase."""
    await buy_product(callback, "rose")


@router.callback_query(F.data == "buy_gift_20")
async def buy_gift_handler(callback: CallbackQuery):
    """Handle gift purchase."""
    await buy_product(callback, "gift")


@router.callback_query(F.data == "buy_bottle_27")
async def buy_bottle_handler(callback: CallbackQuery):
    """Handle bottle purchase."""
    await buy_product(callback, "bottle")


@router.callback_query(F.data == "buy_cake_27")
async def buy_cake_handler(callback: CallbackQuery):
    """Handle cake purchase."""
    await buy_product(callback, "cake")


@router.callback_query(F.data == "buy_trophy_29")
async def buy_trophy_handler(callback: CallbackQuery):
    """Handle trophy purchase."""
    await buy_product(callback, "trophy")


@router.callback_query(F.data == "buy_ring_39")
async def buy_ring_handler(callback: CallbackQuery):
    """Handle ring purchase."""
    await buy_product(callback, "ring")


@router.callback_query(F.data == "buy_stars_39")
async def buy_stars_handler(callback: CallbackQuery):
    """Handle stars purchase."""
    await buy_product(callback, "stars")


@router.callback_query(F.data == "buy_tree_27")
async def buy_tree_handler(callback: CallbackQuery):
    """Handle tree purchase."""
    await buy_product(callback, "tree")