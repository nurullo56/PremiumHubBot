"""Application constants."""

# ===================== PHONE VALIDATION =====================
PHONE_PATTERN = r'^\+?998[0-9]{9}$'

# ===================== BALANCE =====================
BALANCE_SCALE = 100       # 1 olmos = 100 cents (integer precision)
BALANCE_MAX_OLMOS = 1_000_000  # Maximum allowed balance

# ===================== REFERRAL =====================
BONUS_AMOUNT = 1.4          # Bir marta beriladigan referral bonus (olmos)
CHANNEL_LEAVE_DEDUCTION = 0.2  # Har kanal tark etilganda ayriladigan bonus
MAX_SUSPICIOUS_DAYS = 7
MAX_BONUS_RETURNS_PER_DAY = 20

# ===================== ANTI-FRAUD =====================
MAX_REFERRALS_PER_HOUR = 5
MAX_REQUESTS_PER_MINUTE = 20
MULTI_ACCOUNT_THRESHOLD = 3  # Same phone/IP

# ===================== BACKUP =====================
BACKUP_INTERVAL_HOURS = 24
BACKUP_RETENTION_DAYS = 30

# ===================== PREMIUM =====================
PREMIUM_STATUS_PENDING = "pending"
PREMIUM_STATUS_ACTIVE = "active"
PREMIUM_STATUS_REJECTED = "rejected"
PREMIUM_STATUS_CANCELLED = "cancelled"

# ===================== GENDER =====================
GENDER_MALE = "male"
GENDER_FEMALE = "female"

# ===================== SUBSCRIPTION =====================
SUBSCRIPTION_REQUIRED = True

# ===================== DATABASE =====================
DB_TIMEOUT = 30.0  # seconds
DB_MAX_RETRIES = 3
DB_RETRY_DELAY = 0.5  # seconds

# ===================== RATE LIMITING =====================
ANTI_FLOOD_DEFAULT_DELAY = 1.0  # seconds
ANTI_FLOOD_CALLBACK_DELAY = 0.5
ANTI_FLOOD_INLINE_DELAY = 2.0

# ===================== TRANSACTION TYPES =====================
TRANSACTION_REFERRAL_BONUS = "referral_bonus"
TRANSACTION_ADMIN_ADD = "admin_add"
TRANSACTION_ADMIN_SUBTRACT = "admin_subtract"
TRANSACTION_TRANSFER_SENT = "transfer_sent"
TRANSACTION_TRANSFER_RECEIVED = "transfer_received"
TRANSACTION_PROMOCODE = "promocode"
TRANSACTION_PREMIUM_PURCHASE = "premium_purchase"
TRANSACTION_PURCHASE = "purchase"  # ← YANGI: Mahsulot xaridi uchun

# ===================== PROMOCODE TYPES =====================
PROMOCODE_BALANCE = "balance"
PROMOCODE_PREMIUM = "premium"

# ===================== LOGGING =====================
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"