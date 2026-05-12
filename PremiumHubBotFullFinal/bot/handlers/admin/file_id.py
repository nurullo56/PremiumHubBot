# bot/handlers/admin/file_id.py
"""Admin file_id getter handler."""

import logging
from aiogram import Router, F
from bot.filters import IsAdmin
from aiogram.types import Message, Document, PhotoSize
from aiogram.filters import Command

from bot.config import settings

logger = logging.getLogger(__name__)
router = Router(name="admin_file_id")


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in settings.admin_ids


@router.message(IsAdmin(), Command("get_file_id"))
async def get_file_id_command(message: Message):
    """Handle /get_file_id command."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu komanda faqat adminlar uchun!")
        return
    
    await message.answer(
        "📁 <b>FILE ID GETTER</b>\n\n"
        "Iltimos, rasm, video yoki hujjat yuboring.\n"
        "Men sizga uning file_id ni beraman.",
        parse_mode="HTML"
    )


@router.message(F.photo)
async def handle_photo(message: Message):
    """Handle photo and return file_id."""
    if not is_admin(message.from_user.id):
        return
    
    photo: PhotoSize = message.photo[-1]
    file_id = photo.file_id
    file_unique_id = photo.file_unique_id
    
    result = (
        f"🖼 <b>Rasm FILE_ID</b>\n\n"
        f"<code>{file_id}</code>\n\n"
        f"<b>Unique ID:</b>\n"
        f"<code>{file_unique_id}</code>"
    )
    
    await message.answer(result, parse_mode="HTML")
    logger.info(f"📸 Photo file_id sent to admin {message.from_user.id}")


@router.message(F.video)
async def handle_video(message: Message):
    """Handle video and return file_id."""
    if not is_admin(message.from_user.id):
        return
    
    video = message.video
    file_id = video.file_id
    file_unique_id = video.file_unique_id
    
    result = (
        f"🎬 <b>Video FILE_ID</b>\n\n"
        f"<code>{file_id}</code>\n\n"
        f"<b>Unique ID:</b>\n"
        f"<code>{file_unique_id}</code>\n\n"
        f"📏 <b>Size:</b> {video.file_size} bytes"
    )
    
    await message.answer(result, parse_mode="HTML")
    logger.info(f"🎬 Video file_id sent to admin {message.from_user.id}")


@router.message(F.document)
async def handle_document(message: Message):
    """Handle document and return file_id."""
    if not is_admin(message.from_user.id):
        return
    
    document: Document = message.document
    file_id = document.file_id
    file_unique_id = document.file_unique_id
    
    result = (
        f"📄 <b>Document FILE_ID</b>\n\n"
        f"<code>{file_id}</code>\n\n"
        f"<b>Unique ID:</b>\n"
        f"<code>{file_unique_id}</code>\n\n"
        f"📏 <b>Size:</b> {document.file_size} bytes\n"
        f"📝 <b>Name:</b> {document.file_name}"
    )
    
    await message.answer(result, parse_mode="HTML")
    logger.info(f"📄 Document file_id sent to admin {message.from_user.id}")


@router.message(F.animation)
async def handle_animation(message: Message):
    """Handle GIF/animation and return file_id."""
    if not is_admin(message.from_user.id):
        return
    
    animation = message.animation
    file_id = animation.file_id
    file_unique_id = animation.file_unique_id
    
    result = (
        f"🎞 <b>GIF/Animation FILE_ID</b>\n\n"
        f"<code>{file_id}</code>\n\n"
        f"<b>Unique ID:</b>\n"
        f"<code>{file_unique_id}</code>"
    )
    
    await message.answer(result, parse_mode="HTML")
    logger.info(f"🎞 Animation file_id sent to admin {message.from_user.id}")


__all__ = ["router"]