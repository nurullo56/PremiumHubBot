"""User interface text messages."""

# Main menu
MAIN_MENU_WELCOME = """👋 <b>Assalomu alaykum!</b>

🤖 Premium Hub botiga xush kelibsiz!

Quyidagi tugmalardan birini tanlang:"""

# Profile
PROFILE_INFO = """👤 <b>PROFIL</b>

🆔 ID: {user_id}
👤 Ism: {fullname}
📱 Username: @{username}
📞 Telefon: {phone}
💎 Balans: {balance}
👥 Refferallar: {referrals}
⭐ Status: {premium_status}

📅 Ro'yxatdan o'tgan: {registration_date}"""

# Balance
BALANCE_INFO = """💰 <b>BALANS</b>

💎 Sizning balansingiz: {balance}

📊 Oxirgi operatsiyalar:
{history}"""

# Referral
REFERRAL_INFO = """👥 <b>REFERRAL TIZIMI</b>

🔗 Sizning referral havolangiz:
<code>{referral_link}</code>

📊 Statistika:
👥 Taklif qilganlar: {total_referrals}
💰 Bonus: {bonus_amount}💎

💡 Har bir foydalanuvchi uchun {bonus_per_user}💎 olasiz!"""

# Premium
PREMIUM_REQUEST = """⭐ <b>PREMIUM OBUNA</b>

Premium obuna sizga quyidagi imkoniyatlarni beradi:

✅ Maxsus funksiyalar
✅ Prioritet qo'llab-quvvatlash
✅ Reklamasiz foydalanish

💰 Narx: {price}

Admin bilan bog'laning: @{admin_username}"""

PREMIUM_PENDING = "⏳ Premium so'rovingiz ko'rib chiqilmoqda..."
PREMIUM_ACTIVE = "⭐ Sizda Premium obuna mavjud!"
PREMIUM_EXPIRED = "⏰ Premium obunangiz muddati tugadi. Qayta faollashtirish uchun admin bilan bog'laning."

# Promocode
PROMOCODE_INPUT = "🎟️ Promokodni kiriting:"
PROMOCODE_SUCCESS = """✅ <b>Promokod qabul qilindi!</b>

🎁 Mahsulot: {product_name}
💰 Narx: {product_price}

Tez orada sizga aloqaga chiqishadi!"""

# Support
SUPPORT_MESSAGE = """📞 <b>QO'LLAB-QUVVATLASH</b>

Admin bilan bog'laning: @{admin_username}

📧 Email: {email}
🕐 Ish vaqti: 09:00 - 18:00"""
