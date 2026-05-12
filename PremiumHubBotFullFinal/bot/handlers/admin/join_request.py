# bot/handlers/admin/join_request.py
"""Admin join request handlers - zayavka boshqaruvi."""

import logging
from datetime import datetime

from aiogram import Router, F
from bot.filters import IsAdmin
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.database.repositories.join_request_repo import join_request_repo
from bot.keyboards.admin.menu import get_admin_main_keyboard, get_cancel_keyboard

logger = logging.getLogger(__name__)
router = Router(name="admin_join_request")


class AddChatStates(StatesGroup):
    """States for adding managed chat."""
    waiting_for_chat_id = State()
    waiting_for_invite_link = State()
    waiting_for_fullname = State()
    waiting_for_description = State()


class DeleteChatStates(StatesGroup):
    """States for deleting managed chat."""
    waiting_for_chat_id = State()


# ==================== ZAYAVKALAR RO'YXATI ====================

@router.message(IsAdmin(), F.text == "📃 Zayavkalar ro'yxati")
async def show_managed_chats_list(message: Message):
    """Show all managed chats."""
    chats = await join_request_repo.get_all_active_chats()
    
    if not chats:
        await message.answer(
            "📃 <b>Zayavkalar ro'yxati</b>\n\n"
            "❌ Hozircha birorta chat qo'shilmagan.\n\n"
            "Chat qo'shish uchun '➕ Zayavka qo'shish' tugmasini bosing.",
            parse_mode="HTML"
        )
        return
    
    text = "📃 <b>BOSHQARILADIGAN CHATLAR RO'YXATI</b>\n" + "═" * 35 + "\n\n"
    
    for idx, chat in enumerate(chats, 1):
        text += (
            f"{idx}. <b>{chat['fullname']}</b>\n"
            f"├ Chat ID: <code>{chat['chat_id']}</code>\n"
            f"├ Turi: {chat['chat_type']}\n"
            f"├ Status: {'✅ Aktiv' if chat['is_active'] else '❌ Ochirilgan'}\n"
        )
        
        if chat.get('invite_link'):
            text += f"├ Havola: {chat['invite_link']}\n"
        else:
            text += "├ Havola: ❌ Yo'q\n"
        
        if chat.get('description'):
            text += f"└ Tavsif: {chat['description']}\n"
        else:
            text += "└ Tavsif: -\n"
        
        text += "\n"
    
    text += "═" * 35 + f"\n📊 Jami: <b>{len(chats)}</b> ta chat"
    
    await message.answer(text, parse_mode="HTML")


# ==================== ZAYAVKA QO'SHISH ====================

@router.message(IsAdmin(), F.text == "➕ Zayavka qo'shish")
async def add_chat_start(message: Message, state: FSMContext):
    """Start adding new managed chat."""
    await state.set_state(AddChatStates.waiting_for_chat_id)
    await message.answer(
        "➕ <b>Yangi chat qo'shish</b>\n\n"
        "1️⃣ Chat ID ni yuboring.\n\n"
        "Misol: <code>-1001234567890</code>\n\n"
        "💡 Chat ID ni olish uchun:\n"
        "• Botni chatga admin qiling\n"
        "• '🔍 Chat ID aniqlash' tugmasini bosing\n\n"
        "❌ Bekor qilish uchun tugmani bosing",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(IsAdmin(), AddChatStates.waiting_for_chat_id)
async def add_chat_receive_id(message: Message, state: FSMContext):
    """Receive chat ID."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi.",
            reply_markup=get_admin_main_keyboard()
        )
        return

    chat_id = message.text.strip()

    # Validate chat ID format
    if not (chat_id.startswith('-100') and len(chat_id) > 4 and chat_id[4:].isdigit()):
        await message.answer(
            "❌ Noto'g'ri format!\n\n"
            "Chat ID <code>-100</code> bilan boshlanishi kerak.\n"
            "Misol: <code>-1001234567890</code>\n\n"
            "Qaytadan urinib ko'ring:",
            parse_mode="HTML"
        )
        return

    # Check if already exists
    existing = await join_request_repo.get_chat(chat_id)
    if existing:
        await message.answer(
            f"⚠️ Bu chat allaqachon qo'shilgan!\n\n"
            f"Nomi: <b>{existing['fullname']}</b>\n"
            f"Chat ID: <code>{chat_id}</code>",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(chat_id=chat_id)
    await state.set_state(AddChatStates.waiting_for_invite_link)
    
    await message.answer(
        "✅ Chat ID qabul qilindi.\n\n"
        "2️⃣ Endi taklif havolasini yuboring.\n\n"
        "Misol:\n"
        "• <code>https://t.me/+AbCdEfGhIjKl</code>\n"
        "• <code>t.me/+AbCdEfGhIjKl</code>\n\n"
        "💡 Havolani olish uchun:\n"
        "• Chatni oching\n"
        "• ⋮ (3 nuqta) → Invite Links\n"
        "• Create a New Link yoki mavjud linkni nusxalang",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(IsAdmin(), AddChatStates.waiting_for_invite_link)
async def add_chat_receive_invite_link(message: Message, state: FSMContext):
    """Receive invite link."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi.",
            reply_markup=get_admin_main_keyboard()
        )
        return
    
    invite_link = message.text.strip()
    
    # Validate invite link format
    if not ('t.me/' in invite_link or 'telegram.me/' in invite_link):
        await message.answer(
            "❌ Noto'g'ri havola formati!\n\n"
            "Havola <code>t.me/</code> yoki <code>telegram.me/</code> ni o'z ichiga olishi kerak.\n\n"
            "Qaytadan urinib ko'ring:",
            parse_mode="HTML"
        )
        return
    
    # Normalize link
    if not invite_link.startswith('http'):
        invite_link = f"https://{invite_link}"
    
    await state.update_data(invite_link=invite_link)
    await state.set_state(AddChatStates.waiting_for_fullname)
    
    await message.answer(
        "✅ Taklif havolasi qabul qilindi.\n\n"
        "3️⃣ Endi chat nomini yuboring:\n\n"
        "Misol: <b>Premium Kanal</b>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(IsAdmin(), AddChatStates.waiting_for_fullname)
async def add_chat_receive_fullname(message: Message, state: FSMContext):
    """Receive chat fullname."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi.",
            reply_markup=get_admin_main_keyboard()
        )
        return
    
    fullname = message.text.strip()
    
    if len(fullname) < 3:
        await message.answer(
            "❌ Nom juda qisqa!\n\n"
            "Kamida 3 ta harf kiriting.\n"
            "Qaytadan urinib ko'ring:"
        )
        return
    
    await state.update_data(fullname=fullname)
    await state.set_state(AddChatStates.waiting_for_description)
    
    await message.answer(
        "✅ Nom qabul qilindi.\n\n"
        "4️⃣ Qisqacha tavsif yuboring (ixtiyoriy).\n\n"
        "Yoki '<b>-</b>' yuboring o'tkazib yuborish uchun:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(IsAdmin(), AddChatStates.waiting_for_description)
async def add_chat_receive_description(message: Message, state: FSMContext):
    """Receive description and save chat."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi.",
            reply_markup=get_admin_main_keyboard()
        )
        return
    
    description = None if message.text.strip() in ['-', '—', '_'] else message.text.strip()
    
    data = await state.get_data()
    chat_id = data['chat_id']
    fullname = data['fullname']
    invite_link = data['invite_link']
    
    # Determine chat type
    chat_type = "channel" if chat_id.startswith("-100") else "group"
    
    # Save to database
    success = await join_request_repo.create_chat(
        chat_id=chat_id,
        fullname=fullname,
        chat_type=chat_type,
        invite_link=invite_link,
        added_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        added_by=message.from_user.id,
        description=description
    )
    
    await state.clear()
    
    if success:
        text = (
            "✅ <b>Chat muvaffaqiyatli qo'shildi!</b>\n\n"
            f"📝 Nomi: <b>{fullname}</b>\n"
            f"🆔 Chat ID: <code>{chat_id}</code>\n"
            f"📊 Turi: {chat_type}\n"
            f"🔗 Havola: {invite_link}\n"
        )
        
        if description:
            text += f"📄 Tavsif: {description}\n"
        
        text += (
            "\n💡 Eslatma:\n"
            "• Botni chatga admin qiling\n"
            "• Join requests ni yoqing\n"
            "• Foydalanuvchilar havoladan kirib zayavka yuborishi mumkin"
        )
        
        await message.answer(text, reply_markup=get_admin_main_keyboard(), parse_mode="HTML")
    else:
        await message.answer(
            "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
            reply_markup=get_admin_main_keyboard()
        )


# ==================== ZAYAVKA O'CHIRISH ====================

@router.message(IsAdmin(), F.text == "➖ Zayavka o'chirish")
async def delete_chat_start(message: Message, state: FSMContext):
    """Start deleting managed chat."""
    chats = await join_request_repo.get_all_active_chats()
    
    if not chats:
        await message.answer(
            "❌ O'chiradigan chat yo'q.",
            reply_markup=get_admin_main_keyboard()
        )
        return
    
    text = "➖ <b>Chat o'chirish</b>\n\n" "Qaysi chatni o'chirmoqchisiz?\n\n"
    
    for idx, chat in enumerate(chats, 1):
        text += f"{idx}. <b>{chat['fullname']}</b>\n   <code>{chat['chat_id']}</code>\n\n"
    
    text += "Chat ID ni yuboring:"
    
    await state.set_state(DeleteChatStates.waiting_for_chat_id)
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")


@router.message(IsAdmin(), DeleteChatStates.waiting_for_chat_id)
async def delete_chat_receive_id(message: Message, state: FSMContext):
    """Delete chat by ID."""
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi.",
            reply_markup=get_admin_main_keyboard()
        )
        return
    
    chat_id = message.text.strip()
    
    # Check if exists
    chat = await join_request_repo.get_chat(chat_id)
    
    if not chat:
        await message.answer(
            f"❌ Chat topilmadi: <code>{chat_id}</code>\n\n"
            "Qaytadan urinib ko'ring.",
            parse_mode="HTML"
        )
        return
    
    # Delete (deactivate)
    try:
        from bot.database.base import get_db
        async with get_db() as db:
            await db.execute(
                "UPDATE managed_chats SET is_active = 0 WHERE chat_id = ?",
                (chat_id,)
            )
            await db.commit()
        
        await state.clear()
        await message.answer(
            f"✅ <b>Chat o'chirildi!</b>\n\n"
            f"📝 Nomi: <b>{chat['fullname']}</b>\n"
            f"🆔 Chat ID: <code>{chat_id}</code>",
            reply_markup=get_admin_main_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to delete chat: {e}")
        await message.answer(
            "❌ Xatolik yuz berdi.",
            reply_markup=get_admin_main_keyboard()
        )


# ==================== CANCEL HANDLER ====================

@router.message(IsAdmin(), F.text == "❌ Bekor qilish")
async def cancel_action(message: Message, state: FSMContext):
    """Cancel current action."""
    await state.clear()
    await message.answer(
        "❌ Amal bekor qilindi.",
        reply_markup=get_admin_main_keyboard()
    )