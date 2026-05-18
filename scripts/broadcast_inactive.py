"""
Broadcast script — sends a nudge to users who completed registration
(phone given + subscribed to channels) but never used the referral system
(referral_count = 0).

Usage:
    python scripts/broadcast_inactive.py            # real run
    python scripts/broadcast_inactive.py --dry-run  # just count, no messages sent
    python scripts/broadcast_inactive.py --limit 50 # send to first 50 only
"""

import asyncio
import sys
import os
import argparse
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import aiosqlite
import aiohttp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DATABASE_PATH", "database/bot.db")

MESSAGE = (
    "👋 <b>Salom!</b>\n\n"
    "Siz botga ro'yxatdan o'tgansiz, lekin hali <b>BEPUL Telegram Premium</b> "
    "olish imkoniyatidan foydalanmadingiz! 😮\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🎁 <b>Qanday ishlaydi?</b>\n"
    "• Do'stlaringizni taklif qiling\n"
    "• Har bir do'st uchun <b>1.4 olmos</b> olasiz\n"
    "• <b>40 ta do'st</b> = <b>BEPUL Telegram Premium!</b> 🏆\n\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "👇 Boshlash uchun botga qayting va\n"
    "<b>✨BEPUL PREMIUM OLISH💫</b> tugmasini bosing!"
)

# Rate limit: Telegram allows ~30 messages/sec to different users
BATCH_SIZE = 25
DELAY_BETWEEN_BATCHES = 1.1  # seconds


async def get_target_users(db_path: str, limit: int = None):
    """Get users who registered but never used referral system."""
    query = """
        SELECT user_id, fullname, username
        FROM users
        WHERE is_subscribed = 1
          AND (referral_count = 0 OR referral_count IS NULL)
          AND is_blocked = 0
        ORDER BY registration_date DESC
    """
    if limit:
        query += f" LIMIT {limit}"

    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(query)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def send_message(session: aiohttp.ClientSession, token: str, user_id: int, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": user_id,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            if data.get("ok"):
                return True
            # 403 = user blocked bot, 400 = chat not found — skip silently
            error = data.get("description", "")
            if "blocked" in error or "not found" in error or "deactivated" in error:
                return False
            logger.warning(f"  ⚠️  user {user_id}: {error}")
            return False
    except Exception as e:
        logger.error(f"  ❌ user {user_id} request error: {e}")
        return False


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Only count users, don't send")
    parser.add_argument("--limit", type=int, default=None, help="Max users to send to")
    args = parser.parse_args()

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set in .env")
        sys.exit(1)

    logger.info(f"📂 Database: {DB_PATH}")
    users = await get_target_users(DB_PATH, limit=args.limit)
    logger.info(f"🎯 Target users found: {len(users)}")

    if not users:
        logger.info("No users to notify.")
        return

    if args.dry_run:
        logger.info("DRY RUN — no messages will be sent.")
        for u in users[:10]:
            logger.info(f"  • {u['user_id']} {u['fullname']} @{u.get('username', '-')}")
        if len(users) > 10:
            logger.info(f"  ... and {len(users) - 10} more")
        return

    sent = 0
    failed = 0
    total = len(users)

    async with aiohttp.ClientSession() as session:
        for i in range(0, total, BATCH_SIZE):
            batch = users[i:i + BATCH_SIZE]
            tasks = [send_message(session, BOT_TOKEN, u["user_id"], MESSAGE) for u in batch]
            results = await asyncio.gather(*tasks)

            batch_sent = sum(results)
            batch_failed = len(results) - batch_sent
            sent += batch_sent
            failed += batch_failed

            progress = min(i + BATCH_SIZE, total)
            logger.info(f"  [{progress}/{total}] sent={sent} failed={failed}")

            if i + BATCH_SIZE < total:
                await asyncio.sleep(DELAY_BETWEEN_BATCHES)

    logger.info(f"\n✅ Done! Sent: {sent} | Failed/blocked: {failed} | Total: {total}")


if __name__ == "__main__":
    asyncio.run(main())
