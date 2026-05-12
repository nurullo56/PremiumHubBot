"""Guide handler - user guide and instructions."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text, Bold, Italic, Code

from bot.keyboards.user.guide import get_guide_keyboard, get_guide_section_keyboard

router = Router()


@router.message(lambda message: message.text == "📝Qo'llanma")
@router.message(Command("guide"))
async def show_guide(message: Message):
    """Show main guide menu."""
    text = Text(
        "📚 **Qo'llanma va Yordam**\n\n",
        "Botdan foydalanish bo'yicha kerakli bo'limni tanlang:\n\n",
        "• ✨ **Premium olish** - Bepul premium qanday olinadi\n",
        "• 💸 **Premium narxlari** - Premium paketlar haqida\n",
        "• ⭐️ **Stars narxlari** - Stars paketlar haqida\n",
        "• 🎁 **Bonus** - Bonuslarni qanday olish mumkin\n",
        "• 👑 **TOP reyting** - Reytingda qanday yuqoriga chiqish\n",
        "• 💳 **Hisob** - Balans va to'lovlar"
    )
    
    await message.answer(
        text.as_html(),
        reply_markup=get_guide_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data.startswith("guide_"))
async def handle_guide_section(callback: CallbackQuery):
    """Handle guide section selection."""
    section = callback.data.split("_")[1]
    
    guides = {
        "premium": {
            "title": "✨ Premium olish",
            "content": (
                "Premium qanday olinadi:\n\n"
                "1️⃣ Do'stlaringizni botga taklif qiling\n"
                "2️⃣ Har bir taklif uchun bonus oling\n"
                "3️⃣ Reytingda yuqori o'ringa chiqing\n"
                "4️⃣ Promokodlarni ishlating\n\n"
                "💡 Premium funksiyalari:\n"
                "• Cheksiz foydalanish\n"
                "• Tez yuklash\n"
                "• Maxsus imkoniyatlar"
            )
        },
        "prices": {
            "title": "💸 Premium narxlari",
            "content": (
                "Premium paketlar:\n\n"
                "📅 KUNLIK - 10 000 so'm\n"
                "📆 OYLIK - 50 000 so'm\n"
                "🎯 3 OYLIK - 120 000 so'm\n"
                "🌟 YILLIK - 400 000 so'm\n\n"
                "To'lov usullari:\n"
                "• Click, Payme, Apelsin\n"
                "• Karta orqali to'lov"
            )
        },
        "stars": {
            "title": "⭐️ Stars narxlari",
            "content": (
                "Stars paketlari:\n\n"
                "⭐ 100 Stars - 5 000 so'm\n"
                "⭐ 500 Stars - 20 000 so'm\n"
                "⭐ 1000 Stars - 35 000 so'm\n"
                "⭐ 5000 Stars - 150 000 so'm\n\n"
                "Stars bilan nima qilish mumkin:\n"
                "• Premium sotib olish\n"
                "• Maxsus funksiyalar"
            )
        },
        "bonus": {
            "title": "🎁 Bonus",
            "content": (
                "Bonus olish usullari:\n\n"
                "✅ Kunlik bonus - har kuni bosing\n"
                "✅ Referral bonus - do'stlarni taklif qiling\n"
                "✅ Reyting bonusi - TOP 10 ga kiring\n"
                "✅ Promokod - maxsus kodlarni ishlating\n\n"
                "Har bir taklif uchun +1000 so'm bonus!"
            )
        },
        "rating": {
            "title": "👑 TOP reyting",
            "content": (
                "Reytingda qanday yuqoriga chiqish:\n\n"
                "📊 Ballar qanday beriladi:\n"
                "• Do'st taklifi - 10 ball\n"
                "• Premium sotib olish - 100 ball\n"
                "• Har kungi bonus - 5 ball\n"
                "• Promokod - 20 ball\n\n"
                "🏆 TOP 10 har oy sovg'alar oladi!"
            )
        },
        "balance": {
            "title": "💳 Hisob va to'lovlar",
            "content": (
                "Hisob va to'lovlar:\n\n"
                "💰 Balansni to'ldirish:\n"
                "• Administratorga murojaat qiling\n"
                "• @AdminUsername - yozing\n\n"
                "📊 Balansdan foydalanish:\n"
                "• Premium sotib olish\n"
                "• Maxsus funksiyalar\n\n"
                "❓ Savol va muammolar:\n"
                "Admin bilan bog'lanib yeching"
            )
        }
    }
    
    if section in guides:
        text = Text(
            Bold(guides[section]["title"]),
            "\n\n",
            guides[section]["content"],
            "\n\n",
            Italic("Qo'shimcha savollar bo'lsa, admin bilan bog'lanishingiz mumkin.")
        )
        
        await callback.message.edit_text(
            text.as_html(),
            reply_markup=get_guide_section_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(lambda c: c.data == "guide_back")
async def back_to_guide_menu(callback: CallbackQuery):
    """Back to main guide menu."""
    text = Text(
        "📚 **Qo'llanma va Yordam**\n\n",
        "Botdan foydalanish bo'yicha kerakli bo'limni tanlang:"
    )
    
    await callback.message.edit_text(
        text.as_html(),
        reply_markup=get_guide_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()