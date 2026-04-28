"""Admin panel text messages."""

# Main menu
ADMIN_MENU = """👨‍💼 <b>ADMIN PANEL</b>

Kerakli bo'limni tanlang:"""

# Statistics
STATS_MESSAGE = """📊 <b>STATISTIKA</b>

👥 Jami foydalanuvchilar: {total_users:,}
✅ Obuna bo'lganlar: {subscribed_users:,}
📱 Telefon berganlar: {users_with_phone:,}
💰 Balansi borlar: {users_with_balance:,}
💎 Umumiy balans: {total_balance:,.0f}
🔗 Umumiy referrallar: {total_referrals:,}

👤 Erkaklar: {male_users:,}
👩 Ayollar: {female_users:,}

⭐ Premium foydalanuvchilar: {premium_users:,}
⏳ Kutilayotgan so'rovlar: {pending_requests:,}"""

# Broadcast
BROADCAST_START = """📢 <b>XABAR YUBORISH</b>

Yubormoqchi bo'lgan xabaringizni kiriting:"""

BROADCAST_TARGET = """🎯 <b>KIMGA YUBORISH?</b>

Tanlang:
• Hammaga
• Premium foydalanuvchilarga"""

BROADCAST_CONFIRM = """✅ <b>TASDIQLASH</b>

📨 Xabar: 
{message}

👥 Qabul qiluvchilar: {count:,} ta

Yuborilsinmi?"""

BROADCAST_PROGRESS = """📤 <b>YUBORILMOQDA...</b>

Yuborildi: {sent}/{total}
❌ Xato: {failed}
🚫 Blok qilgan: {blocked}"""

BROADCAST_COMPLETE = """✅ <b>YUBORISH YAKUNLANDI!</b>

📊 Natija:
✅ Yuborildi: {sent:,}
❌ Xato: {failed:,}
🚫 Blok qilgan: {blocked:,}"""

# Channel management
CHANNEL_LIST = """📢 <b>KANALLAR</b>

Majburiy obuna kanallari:

{channels}

Jami: {count} ta kanal"""

CHANNEL_ADD_PROMPT = """➕ <b>KANAL QO'SHISH</b>

Kanal ma'lumotlarini quyidagi formatda kiriting:

<code>channel_id | channel_name | channel_url</code>

Namuna:
<code>-100123456789 | Test Channel | https://t.me/testchannel</code>"""

CHANNEL_ADDED = "✅ Kanal qo'shildi!"
CHANNEL_REMOVED = "✅ Kanal o'chirildi!"
CHANNEL_ACTIVATED = "✅ Kanal faollashtirildi!"
CHANNEL_DEACTIVATED = "⏸️ Kanal to'xtatildi!"

# User management
USER_INFO = """👤 <b>FOYDALANUVCHI MA'LUMOTI</b>

🆔 ID: {user_id}
👤 Ism: {fullname}
📱 Username: @{username}
📞 Telefon: {phone}
💎 Balans: {balance}
👥 Referrallar: {referrals}
⭐ Premium: {premium_status}
🚫 Bloklangan: {is_blocked}

📅 Ro'yxatdan: {registration_date}
🕐 Oxirgi faollik: {last_activity}"""

USER_BLOCKED = "🚫 Foydalanuvchi bloklandi!"
USER_UNBLOCKED = "✅ Foydalanuvchi blokdan chiqarildi!"

# Premium management
PREMIUM_REQUESTS = """⭐ <b>PREMIUM SO'ROVLAR</b>

Kutilayotgan so'rovlar: {count}

{requests}"""

PREMIUM_APPROVED = "✅ Premium tasdiqlandi!"
PREMIUM_REJECTED = "❌ Premium rad etildi!"
