"""
Admin test commands for development and debugging.
"""

import logging
from aiogram import Router, F
from bot.filters import IsAdmin
from aiogram.types import Message
from aiogram.filters import Command

from bot.config import settings
from bot.database.repositories.user_repo import user_repo
from bot.database.repositories.balance_repo import balance_repo
from bot.database.repositories.referral_bonus_repo import (
    get_active_referrals_count,
    reset_bonus_flag
)
from bot.database.repositories.premium_repo import premium_repo
from decimal import Decimal

router = Router(name="admin_test")
logger = logging.getLogger(__name__)


# ===================== SET TEST REFERRALS =====================

async def set_test_referrals(user_id: int, count: int) -> bool:
    """Set test referral count for a user."""
    try:
        success = await user_repo.update(user_id, {'referral_count': count})
        if success:
            logger.info(f"✅ Test referrals set: {user_id} -> {count}")
        return success
    except Exception as e:
        logger.error(f"❌ Set test referrals error: {e}")
        return False


async def set_test_balance(user_id: int, amount: float) -> bool:
    """Set test balance for a user."""
    try:
        success = await balance_repo.set_balance(user_id, Decimal(str(amount)))
        if success:
            logger.info(f"✅ Test balance set: {user_id} -> {amount}")
        return success
    except Exception as e:
        logger.error(f"❌ Set test balance error: {e}")
        return False


async def get_user_referrals(user_id: int) -> int:
    """Get user's active referral count."""
    try:
        count = await get_active_referrals_count(user_id)
        return count
    except Exception as e:
        logger.error(f"❌ Get referrals error: {e}")
        return 0


async def get_user_balance(user_id: int) -> float:
    """Get user's balance."""
    try:
        balance = await balance_repo.get_balance(user_id)
        return float(balance)
    except Exception as e:
        logger.error(f"❌ Get balance error: {e}")
        return 0.0


async def get_premium_status(user_id: int) -> str:
    """Get user's premium status."""
    try:
        status = await premium_repo.get_active_premium(user_id)
        return "✅ Active" if status else "❌ None"
    except Exception as e:
        logger.error(f"❌ Get premium status error: {e}")
        return "❌ Error"


async def reset_premium_test(user_id: int) -> bool:
    """Reset premium status for testing."""
    try:
        # Delete all premium records
        from bot.database.base import get_db
        async with get_db() as db:
            await db.execute(
                "DELETE FROM premium WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
        
        # Reset bonus flag
        await reset_bonus_flag(user_id)
        
        logger.info(f"✅ Premium reset: {user_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Reset premium error: {e}")
        return False


# ===================== TEST COMMANDS =====================

@router.message(IsAdmin(), Command("test55"))
async def test_55_referrals(message: Message):
    """TEST: Give yourself 55 referrals + 100 balance."""
    
    user_id = message.from_user.id

    # Set referrals
    ref_success = await set_test_referrals(user_id, 55)
    
    # Set balance
    balance_success = await set_test_balance(user_id, 100)
    
    if ref_success and balance_success:
        referrals = await get_user_referrals(user_id)
        balance = await get_user_balance(user_id)
        
        await message.answer(
            f"✅ TEST muvaffaqiyatli!\n\n"
            f"🆔 User ID: <code>{user_id}</code>\n"
            f"👥 Referallar: <b>{referrals}</b>\n"
            f"💰 Balans: <b>{balance} olmos</b>\n\n"
            f"Endi '✨BEPUL PREMIUM OLISH💫' tugmasini bosing!",
            parse_mode="HTML"
        )
    else:
        await message.answer("❌ Xatolik yuz berdi!")


@router.message(IsAdmin(), Command("testset"))
async def test_set_referrals(message: Message):
    """TEST: Set referral count for any user."""
    
    try:
        # /testset 123456 40
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer(
                "❌ <b>Format:</b> /testset user_id count\n\n"
                "<b>Misol:</b> <code>/testset 123456 40</code>",
                parse_mode="HTML"
            )
            return
        
        user_id = int(parts[1])
        count = int(parts[2])
        
        success = await set_test_referrals(user_id, count)
        
        if success:
            await message.answer(
                f"✅ TEST muvaffaqiyatli!\n\n"
                f"🆔 User ID: <code>{user_id}</code>\n"
                f"👥 Referallar: <b>{count}</b>",
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Xatolik yuz berdi!")
    
    except ValueError:
        await message.answer("❌ User ID va count son bo'lishi kerak!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")


@router.message(IsAdmin(), Command("testgive"))
async def test_give_all(message: Message):
    """
    TEST: Give user both referrals and balance.
    Format: /testgive user_id referrals balance
    Example: /testgive 123456 55 100
    """
    
    try:
        parts = message.text.split()
        
        if len(parts) < 4:
            await message.answer(
                "❌ <b>Format:</b> /testgive user_id referrals balance\n\n"
                "<b>Misol:</b>\n"
                "<code>/testgive 123456 55 100</code>\n\n"
                "Bu user 123456 ga:\n"
                "• 55 ta referal\n"
                "• 100 olmos beradi",
                parse_mode="HTML"
            )
            return
        
        user_id = int(parts[1])
        referrals = int(parts[2])
        balance = int(parts[3])
        
        # Set referrals
        ref_success = await set_test_referrals(user_id, referrals)
        
        # Set balance
        balance_success = await set_test_balance(user_id, balance)
        
        if ref_success and balance_success:
            # Get final values
            final_refs = await get_user_referrals(user_id)
            final_balance = await get_user_balance(user_id)
            
            await message.answer(
                f"✅ <b>TEST muvaffaqiyatli!</b>\n\n"
                f"🆔 User ID: <code>{user_id}</code>\n"
                f"👥 Referallar: <b>{final_refs}</b>\n"
                f"💰 Balans: <b>{final_balance} olmos</b>\n\n"
                f"✨ User endi premium olishi mumkin!",
                parse_mode="HTML"
            )
            
            logger.info(f"✅ TESTGIVE: user {user_id} -> {referrals} ref + {balance} olmos")
        else:
            await message.answer("❌ Xatolik yuz berdi!")
    
    except ValueError:
        await message.answer(
            "❌ <b>Xatolik!</b>\n\n"
            "User ID, referrals va balance <b>son</b> bo'lishi kerak!\n\n"
            "<b>To'g'ri format:</b>\n"
            "<code>/testgive 123456 55 100</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"❌ TESTGIVE xatolik: {e}")
        await message.answer(f"❌ Xatolik: {str(e)}")


@router.message(IsAdmin(), Command("testreset"))
async def test_reset_premium(message: Message):
    """TEST: Reset premium status."""
    
    try:
        # /testreset or /testreset 123456
        parts = message.text.split()
        
        if len(parts) > 1:
            user_id = int(parts[1])
        else:
            user_id = message.from_user.id
        
        success = await reset_premium_test(user_id)
        
        if success:
            status = await get_premium_status(user_id)
            referrals = await get_user_referrals(user_id)
            
            await message.answer(
                f"✅ <b>Premium holati reset qilindi!</b>\n\n"
                f"🆔 User ID: <code>{user_id}</code>\n"
                f"💎 Status: <b>{status}</b>\n"
                f"👥 Referallar: <b>{referrals}</b>\n\n"
                f"Endi qaytadan test qilishingiz mumkin!",
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Xatolik yuz berdi!")
    
    except ValueError:
        await message.answer("❌ User ID son bo'lishi kerak!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")


@router.message(IsAdmin(), Command("testbalance"))
async def test_balance(message: Message):
    """TEST: Set test balance."""
    
    try:
        # /testbalance or /testbalance 123456 100
        parts = message.text.split()
        
        if len(parts) >= 3:
            user_id = int(parts[1])
            amount = int(parts[2])
        elif len(parts) == 2:
            user_id = message.from_user.id
            amount = int(parts[1])
        else:
            user_id = message.from_user.id
            amount = 100
        
        success = await set_test_balance(user_id, amount)
        
        if success:
            balance = await get_user_balance(user_id)
            
            await message.answer(
                f"✅ <b>Test balans berildi!</b>\n\n"
                f"🆔 User ID: <code>{user_id}</code>\n"
                f"💎 Balans: <b>{balance} olmos</b>",
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Xatolik yuz berdi!")
    
    except ValueError:
        await message.answer("❌ User ID va amount son bo'lishi kerak!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")


@router.message(IsAdmin(), Command("testinfo"))
async def test_info(message: Message):
    """TEST: View user information."""
    
    try:
        # /testinfo or /testinfo 123456
        parts = message.text.split()
        
        if len(parts) > 1:
            user_id = int(parts[1])
        else:
            user_id = message.from_user.id
        
        referrals = await get_user_referrals(user_id)
        status = await get_premium_status(user_id)
        balance = await get_user_balance(user_id)
        
        await message.answer(
            f"📊 <b>TEST INFO</b>\n\n"
            f"🆔 User ID: <code>{user_id}</code>\n"
            f"👥 Referallar: <b>{referrals}</b>\n"
            f"💎 Premium status: <b>{status}</b>\n"
            f"💰 Balans: <b>{balance} olmos</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Test komandalar:</b>\n\n"
            f"<code>/test55</code> - O'zingizga 55 referal + 100 olmos\n"
            f"<code>/testset user_id count</code> - Faqat referal\n"
            f"<code>/testbalance user_id amount</code> - Faqat balans\n"
            f"<code>/testgive user_id refs balance</code> - Ikkalasi ham\n"
            f"<code>/testreset [user_id]</code> - Premium reset\n"
            f"<code>/testinfo [user_id]</code> - Ma'lumot",
            parse_mode="HTML"
        )
    
    except ValueError:
        await message.answer("❌ User ID son bo'lishi kerak!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")


@router.message(IsAdmin(), Command("testhelp"))
async def test_help(message: Message):
    """TEST: Help."""
    
    await message.answer(
        "🧪 <b>TEST KOMANDALAR</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<b>O'zingizga:</b>\n"
        "• <code>/test55</code> - 55 referal + 100 olmos\n\n"
        
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Boshqalarga:</b>\n"
        "• <code>/testgive USER_ID REFS BALANCE</code>\n"
        "  Misol: <code>/testgive 123456 55 100</code>\n\n"
        
        "• <code>/testset USER_ID COUNT</code> - Faqat referal\n"
        "  Misol: <code>/testset 123456 40</code>\n\n"
        
        "• <code>/testbalance USER_ID AMOUNT</code> - Faqat balans\n"
        "  Misol: <code>/testbalance 123456 200</code>\n\n"
        
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<b>Boshqa:</b>\n"
        "• <code>/testreset [USER_ID]</code> - Premium reset\n"
        "• <code>/testinfo [USER_ID]</code> - Ma'lumot\n\n"
        
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Barcha komandalar faqat adminlar uchun</i>",
        parse_mode="HTML"
    )


__all__ = ["router"]
