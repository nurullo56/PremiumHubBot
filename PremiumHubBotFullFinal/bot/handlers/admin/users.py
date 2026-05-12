# bot/handlers/admin/users.py
"""Admin user management."""

import logging
import asyncio
from decimal import Decimal

from aiogram import Router, F, Bot
from bot.filters import IsAdmin
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.admin.admin_service import admin_service
from bot.services.finance.balance_service import balance_service
from bot.services.referral.referral_service import referral_service
from bot.services.premium.premium_service import premium_service
from bot.database.repositories.user_repo import user_repo
from bot.keyboards.admin.user_management import get_user_management_keyboard
from bot.keyboards.admin.menu import get_admin_main_keyboard
from bot.states.admin.user_management import UserManagementStates
from bot.texts.admin.messages import ADMIN_MENU
from bot.config import settings

logger = logging.getLogger(__name__)
router = Router(name="admin_users")


# ==================== HELPER FUNCTIONS ====================

async def cancel_and_return_to_admin(message: Message, state: FSMContext):
    """Cancel current operation and return to admin menu."""
    await state.clear()
    
    cancel_msg = await message.answer("❌ Bekor qilindi!")
    await asyncio.sleep(1.5)
    await cancel_msg.delete()
    
    await message.answer(
        ADMIN_MENU,
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )


async def show_user_info_message(message: Message, user_id: int):
    """Show user information in a message."""
    user = await admin_service.get_user_by_id(user_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi!")
        return
    
    balance = await balance_service.get_balance(user_id)
    referrals = await referral_service.get_referral_count(user_id)
    
    premium_status = user.get('premium_status', 'none')
    is_blocked = user.get('is_blocked', False)
    blocked_text = "✅ Ha" if is_blocked else "❌ Yo'q"
    username_display = user.get('username') or "❌ yo'q"
    phone_display = user.get('phone') or "❌ berilmagan"
    
    # Premium status emojisi
    premium_emoji = {
        'active': '⭐',
        'approved': '⭐',
        'pending': '⏳',
        'none': '⚪'
    }.get(premium_status, '⚪')
    
    text = (
        f"👤 <b>FOYDALANUVCHI MA'LUMOTI</b>\n\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"👤 <b>Ism:</b> {user.get('fullname', 'N/A')}\n"
        f"📱 <b>Username:</b> @{username_display}\n"
        f"📞 <b>Telefon:</b> {phone_display}\n"
        f"💎 <b>Balans:</b> {await balance_service.format_balance(balance)}\n"
        f"👥 <b>Referallar:</b> {referrals}\n"
        f"{premium_emoji} <b>Premium:</b> {premium_status}\n"
        f"🚫 <b>Bloklangan:</b> {blocked_text}\n\n"
        f"📅 <b>Ro'yxatdan:</b> {user.get('registration_date', 'N/A')}\n"
        f"🕐 <b>Oxirgi aktivlik:</b> {user.get('last_activity', 'N/A')}"
    )
    
    await message.answer(
        text,
        reply_markup=get_user_management_keyboard(user_id, is_blocked),
        parse_mode="HTML"
    )


async def update_user_info_message(message: Message, user_id: int):
    """Update existing user info message (for callbacks)."""
    user = await admin_service.get_user_by_id(user_id)
    
    if not user:
        await message.edit_text("❌ Foydalanuvchi topilmadi!")
        return
    
    balance = await balance_service.get_balance(user_id)
    referrals = await referral_service.get_referral_count(user_id)
    
    premium_status = user.get('premium_status', 'none')
    is_blocked = user.get('is_blocked', False)
    blocked_text = "✅ Ha" if is_blocked else "❌ Yo'q"
    username_display = user.get('username') or "❌ yo'q"
    phone_display = user.get('phone') or "❌ berilmagan"
    
    premium_emoji = {
        'active': '⭐',
        'approved': '⭐',
        'pending': '⏳',
        'none': '⚪'
    }.get(premium_status, '⚪')
    
    text = (
        f"👤 <b>FOYDALANUVCHI MA'LUMOTI</b>\n\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"👤 <b>Ism:</b> {user.get('fullname', 'N/A')}\n"
        f"📱 <b>Username:</b> @{username_display}\n"
        f"📞 <b>Telefon:</b> {phone_display}\n"
        f"💎 <b>Balans:</b> {await balance_service.format_balance(balance)}\n"
        f"👥 <b>Referallar:</b> {referrals}\n"
        f"{premium_emoji} <b>Premium:</b> {premium_status}\n"
        f"🚫 <b>Bloklangan:</b> {blocked_text}\n\n"
        f"📅 <b>Ro'yxatdan:</b> {user.get('registration_date', 'N/A')}\n"
        f"🕐 <b>Oxirgi aktivlik:</b> {user.get('last_activity', 'N/A')}"
    )
    
    await message.edit_text(
        text,
        reply_markup=get_user_management_keyboard(user_id, is_blocked),
        parse_mode="HTML"
    )


# ==================== MAIN HANDLERS ====================

@router.message(IsAdmin(), F.text == "👤 Foydalanuvchilar")
async def show_users_menu(message: Message):
    """Show users management menu."""
    total = await user_repo.get_total_count()
    active = await user_repo.get_subscribed_count()
    blocked = await user_repo.get_blocked_count() if hasattr(user_repo, 'get_blocked_count') else 0
    
    await message.answer(
        f"👤 <b>FOYDALANUVCHILAR BOSHQARUVI</b>\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"└ Jami: <b>{total:,}</b> ta\n"
        f"├ Aktiv: <b>{active:,}</b> ta\n"
        f"└ Bloklangan: <b>{blocked:,}</b> ta\n\n"
        f"🔍 <b>Foydalanuvchi ID sini kiriting:</b>\n"
        f"<i>Masalan: 123456789</i>",
        parse_mode="HTML"
    )


@router.message(F.text.regexp(r'^\d+$'))
async def show_user_info(message: Message):
    """Show user info by entered ID."""
    try:
        user_id = int(message.text.strip())
        
        # Send typing indicator
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        await show_user_info_message(message, user_id)
        
    except ValueError:
        await message.answer("❌ Noto'g'ri ID formati! Faqat raqam kiriting.")


# ==================== BLOCK / UNBLOCK HANDLERS ====================

@router.callback_query(F.data.startswith("user_block:"))
async def block_user_callback(callback: CallbackQuery, state: FSMContext):
    """Block user."""
    user_id = int(callback.data.split(":")[1])
    
    # Clear any existing state
    await state.clear()
    
    success = await admin_service.block_user(user_id)
    
    if success:
        logger.info(f"✅ Admin {callback.from_user.id} blocked user {user_id}")
        await callback.answer("✅ Foydalanuvchi bloklandi!", show_alert=True)
        
        # Notify the blocked user
        try:
            await callback.bot.send_message(
                user_id,
                "🚫 <b>SIZ BLOKLANDINGIZ!</b>\n\n"
                "Sizning hisobingiz admin tomonidan bloklangan.\n"
                "Qayta tiklash uchun admin bilan bog'lanishingiz kerak.",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Could not notify blocked user {user_id}: {e}")
        
        # Update the message
        await update_user_info_message(callback.message, user_id)
        
    else:
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("user_unblock:"))
async def unblock_user_callback(callback: CallbackQuery, state: FSMContext):
    """Unblock user."""
    user_id = int(callback.data.split(":")[1])
    
    # Clear any existing state
    await state.clear()
    
    success = await admin_service.unblock_user(user_id)
    
    if success:
        logger.info(f"✅ Admin {callback.from_user.id} unblocked user {user_id}")
        await callback.answer("✅ Foydalanuvchi blokdan chiqarildi!", show_alert=True)
        
        # Notify the unblocked user
        try:
            await callback.bot.send_message(
                user_id,
                "✅ <b>SIZ BLOKDAN CHIQARILDIINGIZ!</b>\n\n"
                "Hisobingiz qayta tiklandi. Botdan foydalanishingiz mumkin.\n"
                "Rahmat! 🎉",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Could not notify unblocked user {user_id}: {e}")
        
        # Update the message
        await update_user_info_message(callback.message, user_id)
        
    else:
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)
    
    await callback.answer()


# ==================== BALANCE MANAGEMENT ====================

@router.callback_query(F.data.startswith("user_add_balance:"))
async def add_balance_callback(callback: CallbackQuery, state: FSMContext):
    """Ask for balance amount to add."""
    user_id = int(callback.data.split(":")[1])
    
    await state.update_data(target_user_id=user_id, action="add")
    await state.set_state(UserManagementStates.waiting_for_balance_amount)
    
    await callback.message.answer(
        "💰 <b>BALANS QO'SHISH</b>\n\n"
        "Qancha balans qo'shmoqchisiz?\n\n"
        "<b>Masalan:</b>\n"
        "• 1000 - 1000 so'm qo'shish\n"
        "• 50000 - 50000 so'm qo'shish\n"
        "• 0 - bekor qilish\n\n"
        "<i>Faqat son kiriting (so'mda):</i>",
        reply_markup=None,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("user_subtract_balance:"))
async def subtract_balance_callback(callback: CallbackQuery, state: FSMContext):
    """Ask for balance amount to subtract."""
    user_id = int(callback.data.split(":")[1])
    
    await state.update_data(target_user_id=user_id, action="subtract")
    await state.set_state(UserManagementStates.waiting_for_balance_amount)
    
    await callback.message.answer(
        "💸 <b>BALANS AYIRISH</b>\n\n"
        "Qancha balans ayirmoqchisiz?\n\n"
        "<b>Masalan:</b>\n"
        "• 500 - 500 so'm ayirish\n"
        "• 1000 - 1000 so'm ayirish\n"
        "• 0 - bekor qilish\n\n"
        "<i>Faqat son kiriting (so'mda):</i>",
        reply_markup=None,
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(UserManagementStates.waiting_for_balance_amount)
async def process_balance_amount(message: Message, state: FSMContext):
    """Process balance amount input."""
    try:
        amount_text = message.text.strip()
        
        # Check for cancellation
        if amount_text == "0" or amount_text.lower() == "bekor":
            await cancel_and_return_to_admin(message, state)
            return
        
        amount = Decimal(amount_text)
        
        if amount <= 0:
            await message.answer("❌ Miqdor 0 dan katta bo'lishi kerak! Qaytadan kiriting:")
            return
        
        data = await state.get_data()
        user_id = data['target_user_id']
        action = data['action']
        
        # Send typing indicator
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        if action == "add":
            success = await admin_service.add_balance(
                user_id, 
                amount, 
                f"Admin {message.from_user.id} tomonidan qo'shildi"
            )
            action_text = f"+{amount:,.0f} so'm"
        else:
            # Check if user has enough balance
            current_balance = await balance_service.get_balance(user_id)
            if current_balance < amount:
                await message.answer(
                    f"❌ Xatolik! Foydalanuvchi balansida yetarli mablag' yo'q.\n\n"
                    f"💎 Joriy balans: {await balance_service.format_balance(current_balance)}\n"
                    f"💸 Ayirmoqchi: {amount:,.0f} so'm\n\n"
                    f"Kamroq miqdor kiriting yoki bekor qilish uchun 0 kiriting."
                )
                return
            
            success = await admin_service.subtract_balance(
                user_id, 
                amount, 
                f"Admin {message.from_user.id} tomonidan ayirildi"
            )
            action_text = f"-{amount:,.0f} so'm"
        
        if success:
            # Clear state
            await state.clear()
            
            # Show success message
            success_msg = await message.answer(f"✅ Balans {action_text}")
            await asyncio.sleep(1.5)
            await success_msg.delete()
            
            # Show updated user info
            new_balance = await balance_service.get_balance(user_id)
            
            await message.answer(
                f"📊 <b>YANGI BALANS</b>\n\n"
                f"🆔 ID: <code>{user_id}</code>\n"
                f"💎 Balans: {await balance_service.format_balance(new_balance)}",
                parse_mode="HTML"
            )
            
            # Show admin menu
            await asyncio.sleep(1)
            await message.answer(
                ADMIN_MENU,
                reply_markup=get_admin_main_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Xatolik yuz berdi! Qaytadan urinib ko'ring.")
        
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat son kiriting (masalan: 1000):")
    except Exception as e:
        logger.error(f"Balance operation error: {e}")
        await message.answer("❌ Kutilmagan xatolik yuz berdi!")


# ==================== PREMIUM MANAGEMENT ====================

@router.callback_query(F.data.startswith("user_give_premium:"))
async def give_premium_callback(callback: CallbackQuery, state: FSMContext):
    """Give premium status to user."""
    user_id = int(callback.data.split(":")[1])
    
    # Clear any existing state
    await state.clear()
    
    # Send typing indicator
    await callback.bot.send_chat_action(callback.message.chat.id, "typing")
    
    success = await premium_service.approve_premium(user_id)
    
    if success:
        logger.info(f"✅ Admin {callback.from_user.id} gave premium to user {user_id}")
        await callback.answer("✅ Premium status berildi!", show_alert=True)
        
        # Notify user
        try:
            await callback.bot.send_message(
                user_id,
                "🎉 <b>TABRIKLAYMIZ!</b>\n\n"
                "⭐ Sizga Premium status berildi!\n\n"
                "<b>Premium imkoniyatlari:</b>\n"
                "• 📈 Ko'proq referal bonuslari\n"
                "• 💎 Maxsus aksiyalar\n"
                "• 🎁 Eksklyuziv takliflar\n\n"
                "Xizmatlardan zavqlaning! 🚀",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Could not notify user {user_id} about premium: {e}")
        
        # Update the message
        await update_user_info_message(callback.message, user_id)
        
    else:
        await callback.answer("❌ Premium berishda xatolik yuz berdi!", show_alert=True)
    
    await callback.answer()


# ==================== DELETE USER ====================

@router.callback_query(F.data.startswith("user_delete:"))
async def delete_user_callback(callback: CallbackQuery, state: FSMContext):
    """Delete user permanently (with confirmation)."""
    user_id = int(callback.data.split(":")[1])
    
    # Ask for confirmation
    user = await user_repo.get_by_id(user_id)
    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
        return
    
    # Create confirmation keyboard
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ HA, O'CHIRISH", callback_data=f"user_delete_confirm:{user_id}"),
            InlineKeyboardButton(text="❌ YO'Q, BEKOR QILISH", callback_data=f"user_delete_cancel:{user_id}")
        ]
    ])
    
    await callback.message.answer(
        f"⚠️ <b>DIQQAT! FOYDALANUVCHINI O'CHIRISH</b>\n\n"
        f"Siz <code>{user_id}</code> ({user.get('fullname', 'N/A')}) foydalanuvchini\n"
        f"<b>BUTUNLAY O'CHIRMOQCHISIZ</b>.\n\n"
        f"🔄 Bu amal bilan:\n"
        f"• Barcha ma'lumotlar o'chadi\n"
        f"• Balans, transaction, referrallar YO'QOLADI\n"
        f"• Qayta tiklab BO'LMAYDI!\n\n"
        f"<b>Ishonchingiz komilmi?</b>",
        reply_markup=confirm_keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("user_delete_confirm:"))
async def delete_user_confirm_callback(callback: CallbackQuery, state: FSMContext):
    """Confirm user deletion."""
    user_id = int(callback.data.split(":")[1])
    
    # Clear state
    await state.clear()
    
    # Send typing indicator
    await callback.bot.send_chat_action(callback.message.chat.id, "typing")
    
    # Get user info before deletion (for logging)
    user = await user_repo.get_by_id(user_id)
    user_name = user.get('fullname', 'Unknown') if user else 'Unknown'
    
    # Delete user
    success = await admin_service.delete_user(user_id)
    
    if success:
        logger.warning(f"⚠️ Admin {callback.from_user.id} DELETED user {user_id} ({user_name})")
        await callback.answer("✅ Foydalanuvchi o'chirildi!", show_alert=True)
        
        # Show admin menu
        await callback.message.delete()
        await callback.message.answer(
            f"✅ <b>FOYDALANUVCHI O'CHIRILDI</b>\n\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"👤 Ism: {user_name}\n\n"
            f"Bu amal qaytarib bo'lmaydi!",
            parse_mode="HTML"
        )
        
        await asyncio.sleep(2)
        await callback.message.answer(
            ADMIN_MENU,
            reply_markup=get_admin_main_keyboard(),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ O'chirishda xatolik yuz berdi!", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("user_delete_cancel:"))
async def delete_user_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Cancel user deletion."""
    user_id = int(callback.data.split(":")[1])
    
    # Clear state
    await state.clear()
    
    # Delete confirmation message
    await callback.message.delete()
    
    # Show user info again
    await update_user_info_message(callback.message, user_id)
    
    await callback.answer("❌ O'chirish bekor qilindi!", show_alert=True)


# ==================== BACK HANDLER ====================

@router.callback_query(IsAdmin(), F.data == "admin_back")
async def admin_back_callback(callback: CallbackQuery, state: FSMContext):
    """Go back to admin menu from user management."""
    # Clear any state
    await state.clear()
    
    # Delete current message
    await callback.message.delete()
    
    # Show admin menu
    await callback.message.answer(
        ADMIN_MENU,
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )
    
    await callback.answer()


# ==================== ERROR HANDLER ====================

@router.errors()
async def admin_error_handler(update, exception, state: FSMContext):
    """Handle errors in admin handlers."""
    logger.error(f"Admin handler error: {exception}")
    
    try:
        # Clear state on error
        await state.clear()
        
        # Try to get chat from update
        if hasattr(update, 'message') and update.message:
            await update.message.answer(
                "❌ Xatolik yuz berdi! Iltimos, qaytadan urinib ko'ring.",
                reply_markup=get_admin_main_keyboard()
            )
        elif hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.message.answer(
                "❌ Xatolik yuz berdi! Iltimos, qaytadan urinib ko'ring.",
                reply_markup=get_admin_main_keyboard()
            )
            await update.callback_query.answer()
    except Exception as e:
        logger.error(f"Error in error handler: {e}")