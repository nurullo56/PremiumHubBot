# bot/handlers/admin/broadcast.py
"""Admin broadcast handlers."""

import logging
import asyncio
from aiogram import Router, F, Bot
from bot.filters import IsAdmin
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.services.admin.broadcast_service import broadcast_service
from bot.states.admin.broadcast import BroadcastStates
from bot.keyboards.admin.broadcast import (
    get_broadcast_target_keyboard,
    get_broadcast_confirm_keyboard,
)
from bot.keyboards.admin.menu import get_cancel_keyboard, get_admin_main_keyboard
from bot.texts.admin.messages import BROADCAST_COMPLETE, ADMIN_MENU

logger = logging.getLogger(__name__)
router = Router(name="admin_broadcast")

TARGET_LABELS = {
    "all":     "👥 Hammaga",
    "male":    "👨 Erkaklarga",
    "female":  "👩 Ayollarga",
    "premium": "⭐ Premium foydalanuvchilarga",
}


# ==================== HELPERS ====================

async def _back_to_admin(message: Message, state: FSMContext):
    await state.clear()
    msg = await message.answer("❌ Bekor qilindi!")
    await asyncio.sleep(2)
    await msg.delete()
    await message.answer(ADMIN_MENU, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")


async def _back_to_admin_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Bekor qilindi!")
    await asyncio.sleep(1)
    await callback.message.delete()
    await callback.message.answer(ADMIN_MENU, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")
    await callback.answer()


# ==================== STEP 1: receive message ====================

@router.message(IsAdmin(), F.text == "📩 Xabar yuborish")
async def start_broadcast(message: Message, state: FSMContext):
    await message.answer(
        "📢 <b>XABAR YUBORISH</b>\n\n"
        "Yubormoqchi bo'lgan xabaringizni yuboring.\n\n"
        "💡 Foydalanuvchi ismini qo'shish uchun <code>{fullname}</code> yozing.\n"
        "<b>Misol:</b> <i>Salom {fullname}! Sizda nima yangilik?</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BroadcastStates.waiting_for_message)


@router.message(BroadcastStates.waiting_for_message, F.text == "❌ Bekor qilish")
async def cancel_step1(message: Message, state: FSMContext):
    await _back_to_admin(message, state)


@router.message(BroadcastStates.waiting_for_message)
async def receive_message(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(message_text=message.text, content_type="text")
    elif message.photo:
        await state.update_data(
            file_id=message.photo[-1].file_id,
            caption=message.caption or "",
            content_type="photo"
        )
    elif message.video:
        await state.update_data(
            file_id=message.video.file_id,
            caption=message.caption or "",
            content_type="video"
        )
    else:
        await message.answer("⚠️ Faqat matn, rasm yoki video yuboring.")
        return

    await message.answer(
        "🎯 <b>KIMGA YUBORISH?</b>",
        reply_markup=get_broadcast_target_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BroadcastStates.waiting_for_target)


# ==================== STEP 2: select target ====================

@router.callback_query(BroadcastStates.waiting_for_target, F.data == "broadcast_cancel")
async def cancel_step2(callback: CallbackQuery, state: FSMContext):
    await _back_to_admin_cb(callback, state)


@router.callback_query(
    BroadcastStates.waiting_for_target,
    F.data.in_({"broadcast_all", "broadcast_male", "broadcast_female", "broadcast_premium"})
)
async def select_target(callback: CallbackQuery, state: FSMContext):
    target = callback.data.replace("broadcast_", "")
    users = await broadcast_service.get_user_ids(target)
    count = len(users)
    await state.update_data(target=target, recipient_count=count)

    data = await state.get_data()
    content_type = data.get('content_type', 'text')
    preview = data.get('message_text', data.get('caption', ''))[:200]
    label = TARGET_LABELS.get(target, target)

    # Show {fullname} hint if placeholder is used
    has_placeholder = '{fullname}' in preview
    placeholder_note = "\n✅ <b>{fullname}</b> placeholder topildi — har kishi o'z ismi bilan oladi" if has_placeholder else ""

    await callback.message.edit_text(
        f"✅ <b>TASDIQLASH</b>\n\n"
        f"👤 Guruh: {label}\n"
        f"📊 Foydalanuvchilar: <b>{count} ta</b>\n"
        f"📄 Tur: {content_type.upper()}"
        f"{placeholder_note}\n\n"
        f"📝 <b>Xabar:</b>\n<code>{preview}</code>",
        reply_markup=get_broadcast_confirm_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BroadcastStates.waiting_for_confirm)
    await callback.answer()


# ==================== STEP 3: confirm & send ====================

@router.callback_query(BroadcastStates.waiting_for_confirm, F.data == "broadcast_cancel")
async def cancel_step3(callback: CallbackQuery, state: FSMContext):
    await _back_to_admin_cb(callback, state)


@router.callback_query(BroadcastStates.waiting_for_confirm, IsAdmin(), F.data == "broadcast_confirm")
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target = data.get('target', 'all')
    content_type = data.get('content_type', 'text')

    await callback.message.edit_text("📤 Yuborilmoqda...")
    await callback.answer()

    try:
        if content_type == "text":
            stats = await broadcast_service.send_broadcast(
                bot=bot,
                message_text=data.get('message_text', ''),
                target=target,
            )
        else:
            stats = await broadcast_service.send_media_broadcast(
                bot=bot,
                file_id=data.get('file_id'),
                content_type=content_type,
                caption=data.get('caption', ''),
                target=target,
            )

        text = BROADCAST_COMPLETE.format(
            sent=stats['sent'],
            failed=stats['failed'],
            blocked=stats['blocked'],
        )
        await callback.message.edit_text(text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Broadcast failed: {e}", exc_info=True)
        await callback.message.edit_text(f"❌ Xatolik: {e}", parse_mode="HTML")

    await asyncio.sleep(2)
    await callback.message.answer(ADMIN_MENU, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")
    await state.clear()
