# bot/handlers/admin/stats.py
"""Admin statistics handlers."""

import logging
from datetime import datetime
from io import BytesIO

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from bot.filters import IsAdmin
from bot.services.admin.statistics_service import statistics_service
from bot.keyboards.admin.stats import get_stats_keyboard, get_detailed_stats_keyboard
from bot.keyboards.admin.menu import get_admin_main_keyboard
from bot.texts.admin.messages import ADMIN_MENU

logger = logging.getLogger(__name__)
router = Router(name="admin_stats")


async def format_number(num: int) -> str:
    """Format number with spaces."""
    return f"{num:,}".replace(",", " ")


async def create_progress_bar(percentage: float, width: int = 10) -> str:
    """Create progress bar."""
    filled = int(width * percentage / 100)
    empty = width - filled
    return "█" * filled + "░" * empty


@router.message(IsAdmin(), F.text == "📊 Statistika")
async def show_statistics(message: Message):
    """Show bot statistics overview."""
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    stats = await statistics_service.get_overview()
    
    if not stats:
        await message.answer(
            "❌ Statistikani yuklab bo'lmadi!\n\n"
            "Iltimos, keyinroq qaytadan urinib ko'ring.",
            reply_markup=get_admin_main_keyboard()
        )
        return
    
    total_users = stats.get('total_users', 0)
    active_users = stats.get('subscribed_users', 0)
    users_with_phone = stats.get('users_with_phone', 0)
    users_with_balance = stats.get('users_with_balance', 0)
    total_balance = stats.get('total_balance', 0)
    total_referrals = stats.get('total_referrals', 0)
    active_channels = stats.get('active_channels', 0)
    unused_promocodes = stats.get('unused_promocodes', 0)
    pending_premium = stats.get('pending_premium', 0)
    active_premium = stats.get('active_premium', 0)
    male_users = stats.get('male_users', 0)
    female_users = stats.get('female_users', 0)
    blocked_users = stats.get('blocked_users', 0)
    
    active_percentage = (active_users / total_users * 100) if total_users > 0 else 0
    phone_percentage = (users_with_phone / total_users * 100) if total_users > 0 else 0
    premium_percentage = (active_premium / total_users * 100) if total_users > 0 else 0
    
    active_bar = await create_progress_bar(active_percentage, 15)
    phone_bar = await create_progress_bar(phone_percentage, 15)
    premium_bar = await create_progress_bar(premium_percentage, 15)
    
    text = (
        f"📊 <b>BOT STATISTIKASI</b>\n"
        f"{'═' * 35}\n\n"
        
        f"👥 <b>FOYDALANUVCHILAR</b>\n"
        f"├ Jami: <b>{await format_number(total_users)}</b>\n"
        f"├ Aktiv: <b>{await format_number(active_users)}</b> {active_bar}\n"
        f"├ Telefonli: <b>{await format_number(users_with_phone)}</b> {phone_bar}\n"
        f"├ Balansli: <b>{await format_number(users_with_balance)}</b>\n"
        f"├ Erkak: <b>{await format_number(male_users)}</b>\n"
        f"├ Ayol: <b>{await format_number(female_users)}</b>\n"
        f"└ Bloklangan: <b>{await format_number(blocked_users)}</b>\n\n"
        
        f"💰 <b>MOLIYA</b>\n"
        f"├ Jami balans: <b>{await format_number(int(total_balance))}</b> so'm\n"
        f"└ Balansli userlar: <b>{await format_number(users_with_balance)}</b>\n\n"
        
        f"⭐ <b>PREMIUM</b>\n"
        f"├ Aktiv: <b>{await format_number(active_premium)}</b> {premium_bar}\n"
        f"└ Kutilayotgan: <b>{await format_number(pending_premium)}</b>\n\n"
        
        f"👥 <b>REFERRAL TIZIMI</b>\n"
        f"└ Jami referallar: <b>{await format_number(total_referrals)}</b>\n\n"
        
        f"📢 <b>KANALLAR</b>\n"
        f"└ Aktiv kanallar: <b>{await format_number(active_channels)}</b>\n\n"
        
        f"🎟 <b>PROMOKODLAR</b>\n"
        f"└ Ishlatilmagan: <b>{await format_number(unused_promocodes)}</b>\n\n"
        
        f"{'═' * 35}\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    await message.answer(text, reply_markup=get_stats_keyboard(), parse_mode="HTML")


@router.callback_query(IsAdmin(), F.data == "stats_overview")
async def stats_overview_callback(callback: CallbackQuery):
    """Refresh overview statistics."""
    await callback.answer("🔄 Yangilanmoqda...")
    
    stats = await statistics_service.get_overview()
    
    if not stats:
        await callback.message.edit_text(
            "❌ Statistikani yuklab bo'lmadi!",
            reply_markup=get_stats_keyboard()
        )
        return
    
    total_users = stats.get('total_users', 0)
    active_users = stats.get('subscribed_users', 0)
    users_with_phone = stats.get('users_with_phone', 0)
    users_with_balance = stats.get('users_with_balance', 0)
    total_balance = stats.get('total_balance', 0)
    total_referrals = stats.get('total_referrals', 0)
    active_channels = stats.get('active_channels', 0)
    unused_promocodes = stats.get('unused_promocodes', 0)
    pending_premium = stats.get('pending_premium', 0)
    active_premium = stats.get('active_premium', 0)
    male_users = stats.get('male_users', 0)
    female_users = stats.get('female_users', 0)
    blocked_users = stats.get('blocked_users', 0)
    
    active_percentage = (active_users / total_users * 100) if total_users > 0 else 0
    phone_percentage = (users_with_phone / total_users * 100) if total_users > 0 else 0
    premium_percentage = (active_premium / total_users * 100) if total_users > 0 else 0
    
    active_bar = await create_progress_bar(active_percentage, 15)
    phone_bar = await create_progress_bar(phone_percentage, 15)
    premium_bar = await create_progress_bar(premium_percentage, 15)
    
    text = (
        f"📊 <b>BOT STATISTIKASI</b>\n"
        f"{'═' * 35}\n\n"
        
        f"👥 <b>FOYDALANUVCHILAR</b>\n"
        f"├ Jami: <b>{await format_number(total_users)}</b>\n"
        f"├ Aktiv: <b>{await format_number(active_users)}</b> {active_bar}\n"
        f"├ Telefonli: <b>{await format_number(users_with_phone)}</b> {phone_bar}\n"
        f"├ Balansli: <b>{await format_number(users_with_balance)}</b>\n"
        f"├ Erkak: <b>{await format_number(male_users)}</b>\n"
        f"├ Ayol: <b>{await format_number(female_users)}</b>\n"
        f"└ Bloklangan: <b>{await format_number(blocked_users)}</b>\n\n"
        
        f"💰 <b>MOLIYA</b>\n"
        f"├ Jami balans: <b>{await format_number(int(total_balance))}</b> so'm\n"
        f"└ Balansli userlar: <b>{await format_number(users_with_balance)}</b>\n\n"
        
        f"⭐ <b>PREMIUM</b>\n"
        f"├ Aktiv: <b>{await format_number(active_premium)}</b> {premium_bar}\n"
        f"└ Kutilayotgan: <b>{await format_number(pending_premium)}</b>\n\n"
        
        f"👥 <b>REFERRAL TIZIMI</b>\n"
        f"└ Jami referallar: <b>{await format_number(total_referrals)}</b>\n\n"
        
        f"📢 <b>KANALLAR</b>\n"
        f"└ Aktiv kanallar: <b>{await format_number(active_channels)}</b>\n\n"
        
        f"🎟 <b>PROMOKODLAR</b>\n"
        f"└ Ishlatilmagan: <b>{await format_number(unused_promocodes)}</b>\n\n"
        
        f"{'═' * 35}\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    await callback.message.edit_text(text, reply_markup=get_stats_keyboard(), parse_mode="HTML")


@router.callback_query(IsAdmin(), F.data == "stats_growth")
async def stats_growth_callback(callback: CallbackQuery):
    """Show growth statistics (7 days)."""
    await callback.answer("📈 Yuklanmoqda...")
    
    growth = await statistics_service.get_growth_stats(days=7)
    daily_users = await statistics_service.get_daily_users_chart(7)
    
    if not growth and not daily_users:
        await callback.message.edit_text(
            "❌ O'sish statistikasini yuklab bo'lmadi!",
            reply_markup=get_stats_keyboard()
        )
        return
    
    total_new_users = growth.get('new_users_7d', 0)
    total_transactions = growth.get('transactions_7d', 0)
    
    chart_text = ""
    if daily_users:
        max_count = max((day['count'] for day in daily_users), default=1)
        chart_text = "\n<b>📊 KUNLIK O'SISH:</b>\n"
        
        for day in daily_users:
            date = day['date'][5:]
            count = day['count']
            bar_length = int((count / max_count) * 20) if max_count > 0 else 0
            bar = "█" * bar_length + "░" * (20 - bar_length)
            chart_text += f"\n{date}: {bar} {count}"
    
    text = (
        f"📈 <b>O'SISH STATISTIKASI</b>\n"
        f"{'═' * 35}\n\n"
        
        f"📊 <b>7 KUNLIK NATIJALAR</b>\n"
        f"├ Yangi foydalanuvchilar: <b>+{await format_number(total_new_users)}</b>\n"
        f"└ Tranzaksiyalar: <b>{await format_number(total_transactions)}</b>\n\n"
        
        f"{'─' * 35}"
        f"{chart_text}\n\n"
        
        f"{'═' * 35}\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    await callback.message.edit_text(text, reply_markup=get_detailed_stats_keyboard(), parse_mode="HTML")


@router.callback_query(IsAdmin(), F.data == "stats_detailed")
async def stats_detailed_callback(callback: CallbackQuery):
    """Show detailed statistics."""
    await callback.answer("🔍 Yuklanmoqda...")
    
    overview = await statistics_service.get_overview()
    retention = await statistics_service.get_retention_stats()
    conversion = await statistics_service.get_conversion_funnel()
    
    if not overview:
        await callback.message.edit_text(
            "❌ Batafsil statistikani yuklab bo'lmadi!",
            reply_markup=get_stats_keyboard()
        )
        return
    
    # Retention rates
    retention_day1 = retention.get('day1', {}).get('retention_rate', 0) if retention else 0
    retention_day7 = retention.get('day7', {}).get('retention_rate', 0) if retention else 0
    retention_day30 = retention.get('day30', {}).get('retention_rate', 0) if retention else 0
    
    # Conversion rates
    phone_to_premium = conversion.get('conversion_rates', {}).get('phone_to_premium', 0) if conversion else 0
    premium_to_purchase = conversion.get('conversion_rates', {}).get('premium_to_purchase', 0) if conversion else 0
    overall_conversion = conversion.get('conversion_rates', {}).get('overall', 0) if conversion else 0
    
    day1_bar = await create_progress_bar(retention_day1, 15)
    day7_bar = await create_progress_bar(retention_day7, 15)
    day30_bar = await create_progress_bar(retention_day30, 15)
    
    text = (
        f"🔍 <b>BATAFSIL STATISTIKA</b>\n"
        f"{'═' * 35}\n\n"
        
        f"📊 <b>RETENTION (QAYTISH KO'RSATKICHI)</b>\n"
        f"├ 1 kundan keyin: <b>{retention_day1:.1f}%</b> {day1_bar}\n"
        f"├ 7 kundan keyin: <b>{retention_day7:.1f}%</b> {day7_bar}\n"
        f"└ 30 kundan keyin: <b>{retention_day30:.1f}%</b> {day30_bar}\n\n"
        
        f"🔄 <b>KONVERSIYA VORONKASI</b>\n"
        f"├ Telefon → Premium: <b>{phone_to_premium:.1f}%</b>\n"
        f"├ Premium → Xarid: <b>{premium_to_purchase:.1f}%</b>\n"
        f"└ Umumiy konversiya: <b>{overall_conversion:.1f}%</b>\n\n"
        
        f"📊 <b>QO'SHIMCHA MA'LUMOTLAR</b>\n"
        f"├ Jami foydalanuvchilar: <b>{await format_number(overview.get('total_users', 0))}</b>\n"
        f"├ Aktiv premium: <b>{await format_number(overview.get('active_premium', 0))}</b>\n"
        f"├ Referallar: <b>{await format_number(overview.get('total_referrals', 0))}</b>\n"
        f"└ Jami balans: <b>{await format_number(int(overview.get('total_balance', 0)))}</b> so'm\n\n"
        
        f"{'═' * 35}\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    
    await callback.message.edit_text(text, reply_markup=get_detailed_stats_keyboard(), parse_mode="HTML")


@router.callback_query(IsAdmin(), F.data == "stats_export")
async def stats_export_callback(callback: CallbackQuery):
    """Export statistics as text file."""
    await callback.answer("📄 Eksport qilinmoqda...")
    
    overview = await statistics_service.get_overview()
    growth = await statistics_service.get_growth_stats(days=30)
    daily_users = await statistics_service.get_daily_users_chart(30)
    
    if not overview:
        await callback.message.answer("❌ Statistikani eksport qilib bo'lmadi!")
        return
    
    export_text = []
    export_text.append("=" * 60)
    export_text.append("BOT STATISTIKASI EKSPORT")
    export_text.append(f"Sana: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    export_text.append("=" * 60)
    export_text.append("")
    
    export_text.append("📊 ASOSIY STATISTIKA")
    export_text.append("-" * 40)
    export_text.append(f"Jami foydalanuvchilar: {overview.get('total_users', 0):,}")
    export_text.append(f"Aktiv foydalanuvchilar: {overview.get('subscribed_users', 0):,}")
    export_text.append(f"Telefon tasdiqlaganlar: {overview.get('users_with_phone', 0):,}")
    export_text.append(f"Balansli foydalanuvchilar: {overview.get('users_with_balance', 0):,}")
    export_text.append(f"Jami balans: {int(overview.get('total_balance', 0)):,} so'm")
    export_text.append(f"Jami referallar: {overview.get('total_referrals', 0):,}")
    export_text.append(f"Aktiv kanallar: {overview.get('active_channels', 0):,}")
    export_text.append(f"Aktiv premium: {overview.get('active_premium', 0):,}")
    export_text.append(f"Kutilayotgan premium: {overview.get('pending_premium', 0):,}")
    export_text.append("")
    
    if growth:
        export_text.append("📈 O'SISH (30 KUN)")
        export_text.append("-" * 40)
        export_text.append(f"Yangi foydalanuvchilar: +{growth.get('new_users_30d', 0):,}")
        export_text.append(f"Tranzaksiyalar: {growth.get('transactions_30d', 0):,}")
        export_text.append("")
    
    if daily_users:
        export_text.append("📊 KUNLIK FOYDALANUVCHILAR")
        export_text.append("-" * 40)
        for day in daily_users:
            export_text.append(f"{day['date']}: {day['count']:,} ta")
        export_text.append("")
    
    export_text.append("=" * 60)
    export_text.append("Eksport tugadi")
    
    export_content = "\n".join(export_text)
    file_obj = BytesIO(export_content.encode('utf-8'))
    file_name = f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    await callback.message.answer_document(
        document=BufferedInputFile(file_obj.getvalue(), filename=file_name),
        caption=f"📊 Statistika eksporti\n📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        reply_markup=get_stats_keyboard()
    )


@router.callback_query(IsAdmin(), F.data == "stats_back")
async def stats_back_callback(callback: CallbackQuery):
    """Go back to main statistics menu."""
    await callback.answer("⬅️ Orqaga")
    await stats_overview_callback(callback)


@router.callback_query(IsAdmin(), F.data == "stats_refresh")
async def stats_refresh_callback(callback: CallbackQuery):
    """Refresh current statistics page."""
    await callback.answer("🔄 Yangilanmoqda...")
    await stats_overview_callback(callback)


@router.callback_query(IsAdmin(), F.data == "admin_back")
async def admin_back_from_stats_callback(callback: CallbackQuery):
    """Go back to admin menu from statistics."""
    await callback.message.delete()
    await callback.message.answer(
        ADMIN_MENU,
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()