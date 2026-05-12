# bot/handlers/admin/promocode.py
"""Admin promocode management."""

import logging
import asyncio
from decimal import Decimal

from aiogram import Router, F
from bot.filters import IsAdmin
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.services.promo.promocode_service import promocode_service
from bot.keyboards.admin.promocode import get_promocode_management_keyboard
from bot.keyboards.admin.menu import get_cancel_keyboard, get_admin_main_keyboard
from bot.states.admin.promocode import PromocodeStates
from bot.texts.admin.messages import ADMIN_MENU

logger = logging.getLogger(__name__)
router = Router(name="admin_promocode")


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

@router.message(IsAdmin(), F.text == "🎟 Promokodlar")
async def show_promocode_menu(message: Message):
    """Show promocode management menu."""
    await message.answer(
        "🎟 <b>PROMOKOD BOSHQARUV</b>\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=get_promocode_management_keyboard(),
        parse_mode="HTML"
    )


@router.message(IsAdmin(), F.text == "➕ Promokod yaratish")
async def create_promocode_start(message: Message, state: FSMContext):
    """Start creating a new promocode."""
    await message.answer(
        "🎟 <b>PROMOKOD YARATISH</b>\n\n"
        "Ma'lumotlarni quyidagi formatda kiriting:\n\n"
        "<code>mahsulot_nomi | narx | muddati_kunlarda</code>\n\n"
        "<b>Namuna:</b>\n"
        "<code>Premium 1 oy | 50000 | 30</code>\n\n"
        "<i>Bu promokod avtomatik ravishda yaratiladi va sizga ko'rsatiladi.</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(PromocodeStates.waiting_for_promocode_data)


@router.message(PromocodeStates.waiting_for_promocode_data, F.text == "❌ Bekor qilish")
async def cancel_create_promocode(message: Message, state: FSMContext):
    """Cancel promocode creation."""
    await cancel_and_return_to_admin(message, state)


@router.message(PromocodeStates.waiting_for_promocode_data, F.text)
async def receive_promocode_data(message: Message, state: FSMContext):
    """Receive promocode data and create it."""
    try:
        # Parse input: product_name | price | expiry_days
        parts = [p.strip() for p in message.text.split('|')]
        
        if len(parts) < 3:
            await message.answer(
                "❌ Noto'g'ri format!\n\n"
                "To'g'ri format:\n"
                "<code>Premium 1 oy | 50000 | 30</code>\n\n"
                "Qaytadan urinib ko'ring.",
                parse_mode="HTML"
            )
            return
        
        product_name = parts[0]
        product_price = float(parts[1])
        expiry_days = int(parts[2])
        
        # Create promocode using service
        success, code = await promocode_service.create_promocode(
            user_id=message.from_user.id,
            product_name=product_name,
            product_price=product_price,
            expiry_days=expiry_days,
            usage_limit=1
        )
        
        if success:
            logger.info(f"✅ Promocode created: {code} by admin {message.from_user.id}")
            
            # Show success message with the code
            await message.answer(
                f"✅ <b>PROMOKOD YARATILDI!</b>\n\n"
                f"🎟 Kod: <code>{code}</code>\n"
                f"📦 Mahsulot: {product_name}\n"
                f"💰 Narx: {product_price:,.0f} so'm\n"
                f"⏰ Muddati: {expiry_days} kun\n\n"
                f"<i>Bu promokodni foydalanuvchilarga tarqating!</i>",
                parse_mode="HTML"
            )
            
            # Clear state
            await state.clear()
            
            # Show admin menu after a moment
            await asyncio.sleep(2)
            await message.answer(
                ADMIN_MENU,
                reply_markup=get_admin_main_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Promokod yaratishda xatolik yuz berdi!")
            
    except ValueError as e:
        await message.answer(
            f"❌ Xatolik: {str(e)}\n\n"
            "Narx son bo'lishi kerak va muddat butun son bo'lishi kerak.\n"
            "Qaytadan urinib ko'ring."
        )
    except Exception as e:
        logger.error(f"Error creating promocode: {e}")
        await message.answer("❌ Kutilmagan xatolik yuz berdi!")


@router.message(IsAdmin(), F.text == "📋 Barcha promokodlar")
async def list_all_promocodes(message: Message):
    """List all promocodes."""
    from bot.database.repositories.promocode_repo import promocode_repo
    
    promos = await promocode_repo.get_all()
    
    if not promos:
        await message.answer("📋 Hozircha hech qanday promokod mavjud emas.")
        return
    
    # Format promocode list
    text = "📋 <b>BARCHA PROMOKODLAR</b>\n\n"
    
    for promo in promos[:20]:  # Show max 20
        status = "✅ Aktiv" if not promo.get('is_used') else "❌ Ishlatilgan"
        used_by = f"\n👤 Ishlatgan: {promo.get('used_by')}" if promo.get('used_by') else ""
        
        text += (
            f"🎟 <code>{promo.get('code')}</code>\n"
            f"📦 {promo.get('product_name')}\n"
            f"💰 {promo.get('product_price'):,.0f} so'm\n"
            f"📊 {status}{used_by}\n"
            f"👨‍💼 Yaratgan: {promo.get('user_id')}\n\n"
        )
    
    if len(promos) > 20:
        text += f"\n... va yana {len(promos) - 20} ta promokod"
    
    await message.answer(text, parse_mode="HTML")