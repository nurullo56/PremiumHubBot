"""Chat ID detection handler for admins."""

import logging
from aiogram import Router, F
from bot.filters import IsAdmin
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.admin.menu import get_admin_main_keyboard

logger = logging.getLogger(__name__)
router = Router(name="admin_chat_id")


class ChatIDStates(StatesGroup):
    """States for chat ID detection."""
    waiting_for_forward = State()


@router.message(IsAdmin(), F.text == "🔍 Chat ID aniqlash")
async def start_chat_id_detection(message: Message, state: FSMContext):
    """Start chat ID detection process."""
    await state.set_state(ChatIDStates.waiting_for_forward)
    
    await message.answer(
        "📋 <b>CHAT ID ANIQLASH</b>\n\n"
        "Quyidagi usullardan birini tanlang:\n\n"
        "1️⃣ <b>Kanal/Guruh uchun:</b>\n"
        "   Kanaldan yoki guruhdan <b>istalgan xabarni forward</b> qiling\n\n"
        "2️⃣ <b>Shaxsiy chat uchun:</b>\n"
        "   Foydalanuvchidan xabarni forward qiling\n\n"
        "3️⃣ <b>O'zingizning ID:</b>\n"
        "   /myid yoki istalgan xabar yuboring\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Forward qilish uchun: xabar ustiga bosing → Forward → bu yerga yuboring</i>",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(IsAdmin(), ChatIDStates.waiting_for_forward, F.forward_from_chat)
async def handle_channel_forward(message: Message, state: FSMContext):
    """Handle forwarded message from channel/group."""
    chat = message.forward_from_chat
    
    chat_type_emoji = {
        'channel': '📢',
        'supergroup': '👥',
        'group': '👥',
    }
    
    emoji = chat_type_emoji.get(chat.type, '💬')
    
    # Get chat type in Uzbek
    chat_type_uz = {
        'channel': 'Kanal',
        'supergroup': 'Superguruh',
        'group': 'Guruh',
    }
    type_name = chat_type_uz.get(chat.type, chat.type.capitalize())
    
    response = (
        f"{emoji} <b>{type_name} ma'lumotlari:</b>\n\n"
        f"📋 <b>Nomi:</b> {chat.title}\n"
        f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>\n"
    )
    
    if chat.username:
        response += f"🔗 <b>Username:</b> @{chat.username}\n"
    
    response += (
        f"\n━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 <i>Chat ID ni nusxalash uchun ustiga bosing</i>\n\n"
        f"✅ Yana aniqlash uchun boshqa xabar forward qiling\n"
        f"❌ Chiqish uchun /cancel bosing"
    )
    
    await message.answer(response, parse_mode="HTML")
    await state.clear()


@router.message(IsAdmin(), ChatIDStates.waiting_for_forward, F.forward_from)
async def handle_user_forward(message: Message, state: FSMContext):
    """Handle forwarded message from user."""
    user = message.forward_from
    
    response = (
        f"👤 <b>Foydalanuvchi ma'lumotlari:</b>\n\n"
        f"📋 <b>Ism:</b> {user.full_name}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
    )
    
    if user.username:
        response += f"🔗 <b>Username:</b> @{user.username}\n"
    
    if user.is_bot:
        response += f"🤖 <b>Status:</b> Bot\n"
    
    if user.is_premium:
        response += f"⭐ <b>Premium:</b> Ha\n"
    
    response += (
        f"\n━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 <i>User ID ni nusxalash uchun ustiga bosing</i>\n\n"
        f"✅ Yana aniqlash uchun boshqa xabar forward qiling\n"
        f"❌ Chiqish uchun /cancel bosing"
    )
    
    await message.answer(response, parse_mode="HTML")
    await state.clear()


@router.message(IsAdmin(), ChatIDStates.waiting_for_forward)
async def handle_regular_message(message: Message, state: FSMContext):
    """Handle regular message (user's own ID)."""
    user = message.from_user
    
    response = (
        f"👤 <b>Sizning ma'lumotlaringiz:</b>\n\n"
        f"📋 <b>Ism:</b> {user.full_name}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
    )
    
    if user.username:
        response += f"🔗 <b>Username:</b> @{user.username}\n"
    
    if user.is_premium:
        response += f"⭐ <b>Premium:</b> Ha\n"
    
    response += (
        f"\n━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 <b>Eslatma:</b>\n"
        f"• Kanal/Guruh ID ni olish uchun xabar <b>forward</b> qiling\n"
        f"• Boshqa foydalanuvchi ID uchun uning xabarini forward qiling\n\n"
        f"✅ Qayta urinish uchun forward qiling\n"
        f"❌ Chiqish uchun /cancel bosing"
    )
    
    await message.answer(response, parse_mode="HTML")
    await state.clear()


@router.message(IsAdmin(), F.text == "/myid")
async def show_my_id(message: Message):
    """Show user's own ID (quick command)."""
    user = message.from_user
    
    response = (
        f"👤 <b>Sizning ma'lumotlaringiz:</b>\n\n"
        f"📋 <b>Ism:</b> {user.full_name}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
    )
    
    if user.username:
        response += f"🔗 <b>Username:</b> @{user.username}\n"
    
    if user.is_premium:
        response += f"⭐ <b>Premium:</b> Ha\n"
    
    await message.answer(response, parse_mode="HTML")


__all__ = ["router"]
