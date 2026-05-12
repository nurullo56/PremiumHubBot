"""Registration flow text messages."""

# Welcome
REGISTRATION_START = """👋 <b>Assalomu alaykum!</b>

🤖 Premium Hub botiga xush kelibsiz!

📝 Ro'yxatdan o'tish uchun quyidagi bosqichlarni bajaring:

1️⃣ Captcha
2️⃣ Jins
3️⃣ Telefon raqami
4️⃣ Kanallarga obuna"""

# Captcha
CAPTCHA_PROMPT = """🔐 <b>CAPTCHA</b>

Botdan foydalanishni davom ettirish uchun captcha tekshiruvidan o'ting.

👇 Quyidagi tugmani bosing:"""

CAPTCHA_SUCCESS = "✅ Captcha muvaffaqiyatli o'tdingiz!"
CAPTCHA_FAILED = "❌ Captcha xato! Qaytadan urinib ko'ring."

# Gender
GENDER_PROMPT = """👤 <b>JINS</b>

Jinsingizni tanlang:"""

GENDER_SUCCESS = "✅ Jins saqlandi!"

# Phone
PHONE_PROMPT = """📱 <b>TELEFON RAQAMI</b>

Telefon raqamingizni kiriting:

Namuna: +998901234567"""

PHONE_INVALID = "❌ Telefon raqami noto'g'ri formatda! Qaytadan kiriting."
PHONE_EXISTS = "❌ Bu telefon raqami allaqachon ro'yxatdan o'tgan!"
PHONE_SUCCESS = "✅ Telefon raqami saqlandi!"

# Subscription
SUBSCRIPTION_PROMPT = """📢 <b>KANALLARGA OBUNA</b>

Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:

{channels}

✅ Obuna bo'lganingizdan so'ng "Tekshirish" tugmasini bosing."""

SUBSCRIPTION_CHECK = "🔄 Obunalar tekshirilmoqda..."
SUBSCRIPTION_INCOMPLETE = """❌ <b>Siz hali barcha kanallarga obuna bo'lmadingiz!</b>

Quyidagi kanallarga obuna bo'ling:
{missing_channels}"""

SUBSCRIPTION_SUCCESS = """✅ <b>TABRIKLAYMIZ!</b>

Siz muvaffaqiyatli ro'yxatdan o'tdingiz!

💎 Boshlang'ich balans: 0
👥 Referrallar: 0

Botdan foydalanishni boshlang!"""

# Referral bonus
REFERRAL_BONUS_RECEIVED = """🎁 <b>REFERRAL BONUSI!</b>

Sizni taklif qilgan foydalanuvchi uchun {amount}💎 bonus oldingiz!"""
