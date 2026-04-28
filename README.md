# 🤖 PremiumHubBot

> **Telegram Premium Referral Bot** - Do'stlarni taklif qilish orqali bepul Telegram Premium olish imkoniyati.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-blue.svg)](https://docs.aiogram.dev/)
[![SQLite](https://img.shields.io/badge/database-SQLite-green.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Mundarija

- [Loyiha haqida](#-loyiha-haqida)
- [Asosiy funksiyalar](#-asosiy-funksiyalar)
- [Texnologiyalar](#-texnologiyalar)
- [O'rnatish](#-ornatish)
- [Konfiguratsiya](#-konfiguratsiya)
- [Ishga tushirish](#-ishga-tushirish)
- [Arxitektura](#-arxitektura)
- [Database Schema](#-database-schema)
- [Admin Panel](#-admin-panel)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Loyiha haqida

**PremiumHubBot** — Telegram Premium xizmatlarini referral tizimi orqali ulashuvchi bot. Foydalanuvchilar do'stlarini taklif qilib, olmos to'playdilar va 40 ta do'st to'plaganlarida **BEPUL Telegram Premium** olishadi.

### Asosiy konsepsiya

```
User A → /start → Ro'yxatdan o'tish
  ↓
User A → Referral link olish → https://t.me/bot?start=12345
  ↓
User B → Link orqali kirish → User A ga +1.4 💎
  ↓
User A → 40 ta do'st → 56 💎 → BEPUL Premium (30 kun)
```

---

## ✨ Asosiy funksiyalar

### 👤 User Features

- ✅ **Ro'yxatdan o'tish** — Captcha, jins, telefon raqam
- 🔗 **Referral tizimi** — Shaxsiy taklif linki
- 💎 **Olmos balansi** — 1 do'st = 1.4 olmos
- ⭐ **Premium olish** — 40 do'st = BEPUL Premium
- 📊 **Statistika** — Referrallar soni, progress bar
- 💰 **Balans tarixi** — Barcha tranzaksiyalar
- 🎁 **Promocode** — Maxsus kod orqali bonus

### 👮‍♂️ Admin Features

- 📊 **Statistika** — Foydalanuvchilar, balans, premium
- 📩 **Broadcasting** — Barcha userlarga xabar
- 📢 **Kanal boshqaruv** — Majburiy obuna kanallari
- 🎟 **Promocode** — Yaratish, tahrirlash, statistika
- 👥 **User boshqaruv** — Qidirish, tahrirlash, bloklash
- ⭐ **Premium so'rovlar** — Tasdiqlash/rad etish
- 📃 **Zayavka kanallari** — Auto-approve join requests
- 🧪 **Test komandalar** — Development uchun
- 🔍 **Chat ID aniqlash** — Kanal/guruh ID topish

---

## 🛠 Texnologiyalar

### Core Stack

| Texnologiya | Versiya | Maqsad |
|------------|---------|--------|
| **Python** | 3.11+ | Asosiy dasturlash tili |
| **aiogram** | 3.x | Telegram Bot framework |
| **SQLite** | 3.x | Database |
| **aiosqlite** | 0.20+ | Async SQLite driver |
| **Pydantic** | 2.x | Settings validation |

### Additional Libraries

- **APScheduler** — Background jobs (backup, cleanup)
- **Pillow** — Captcha generation
- **python-dotenv** — Environment variables
- **sentry-sdk** — Error tracking (optional)

---

## 📥 O'rnatish

### 1️⃣ Prerequisites

```bash
# Python 3.11+ kerak
python3 --version

# Git
git --version
```

### 2️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/PremiumHubBot.git
cd PremiumHubBot
```

### 3️⃣ Virtual Environment

```bash
# Virtual environment yaratish
python3 -m venv venv

# Aktivlashtirish (Linux/Mac)
source venv/bin/activate

# Aktivlashtirish (Windows)
venv\Scripts\activate
```

### 4️⃣ Dependencies

```bash
# Requirements o'rnatish
pip install -r requirements.txt
```

---

## ⚙️ Konfiguratsiya

### 1️⃣ Environment Variables

`.env` fayl yarating:

```bash
cp .env.example .env
```

`.env` faylni tahrirlang:

```env
# ============================================
# BOT SETTINGS
# ============================================
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_USERNAME=your_bot_username
ADMIN_ID=123456789

# ============================================
# DATABASE
# ============================================
DATABASE_PATH=bot/database.db

# ============================================
# REFERRAL SETTINGS
# ============================================
REQUIRED_REFERRALS=40
REFERRAL_BONUS=1.4
PREMIUM_COST=56
PREMIUM_DURATION_DAYS=30

# ============================================
# SECURITY
# ============================================
CAPTCHA_EXPIRY_MINUTES=3

# ============================================
# OPTIONAL
# ============================================
ENVIRONMENT=production
SENTRY_DSN=your_sentry_dsn_here
```

### 2️⃣ Admin ID olish

```bash
# Botni ishga tushiring
python -m bot.main

# Telegram da /start bosing
# Logda sizning user_id ni ko'rasiz
```

### 3️⃣ Bot Token olish

1. Telegram da [@BotFather](https://t.me/BotFather) ga boring
2. `/newbot` buyrug'i bering
3. Bot nomini kiriting
4. Bot username kiriting
5. Token oling va `.env` ga qo'ying

---

## 🚀 Ishga tushirish

### Development Mode

```bash
# Bitta komanda
python -m bot.main
```

### Production Mode (systemd)

```bash
# Service file yaratish
sudo nano /etc/systemd/system/premiumhubbot.service
```

```ini
[Unit]
Description=PremiumHubBot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/PremiumHubBot
Environment="PATH=/path/to/PremiumHubBot/venv/bin"
ExecStart=/path/to/PremiumHubBot/venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Service ni yoqish
sudo systemctl daemon-reload
sudo systemctl enable premiumhubbot
sudo systemctl start premiumhubbot

# Status ko'rish
sudo systemctl status premiumhubbot

# Loglarni ko'rish
journalctl -u premiumhubbot -f
```

---

## 🏗 Arxitektura

### Folder Structure

```
PremiumHubBot/
├── bot/
│   ├── config/              # Settings, environment
│   ├── database/            # Database layer
│   │   ├── models/          # Data models
│   │   ├── repositories/    # Data access layer
│   │   └── uow/             # Unit of Work pattern
│   ├── handlers/            # Message/callback handlers
│   │   ├── admin/           # Admin handlers
│   │   ├── premium/         # Referral handlers
│   │   ├── registration/    # Registration flow
│   │   └── user/            # User handlers
│   ├── keyboards/           # Telegram keyboards
│   ├── middlewares/         # Custom middlewares
│   ├── services/            # Business logic
│   ├── states/              # FSM states
│   ├── texts/               # Text templates
│   ├── utils/               # Utilities
│   ├── filters/             # Custom filters
│   └── main.py              # Entry point
├── jobs/                    # Background jobs
├── backups/                 # Database backups
├── logs/                    # Log files
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

### Architecture Layers

```
┌─────────────────────────────────────────┐
│          PRESENTATION LAYER             │
│  (Handlers - User/Admin/Premium)        │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│          SERVICE LAYER                  │
│  (Business Logic - Referral, Channel)   │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│          REPOSITORY LAYER               │
│  (Data Access - Repo Pattern)           │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│          DATABASE LAYER                 │
│  (SQLite + aiosqlite)                   │
└─────────────────────────────────────────┘
```

### Design Patterns

- ✅ **Repository Pattern** — Data access abstraction
- ✅ **Service Layer** — Business logic separation
- ✅ **Unit of Work** — Transaction management
- ✅ **Filter Pattern** — Custom aiogram filters
- ✅ **Singleton** — Configuration, bot instance
- ✅ **FSM** — Conversation states

---

## 💾 Database Schema

### Main Tables

#### `users`
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    gender TEXT,
    language_code TEXT DEFAULT 'uz',
    is_premium INTEGER DEFAULT 0,
    is_blocked INTEGER DEFAULT 0,
    is_subscribed INTEGER DEFAULT 0,
    captcha_verified INTEGER DEFAULT 0,
    referred_by INTEGER,
    referral_bonus_given INTEGER DEFAULT 0,
    referral_count INTEGER DEFAULT 0,
    registration_date TEXT,
    last_activity TEXT
);
```

---

## 👮‍♂️ Admin Panel

### Admin komandalar

| Komanda | Ta'rif |
|---------|--------|
| `/admin` | Admin panel ochish |
| `/test55` | Test: 55 referral + 100 olmos |

---

## 🚀 Deployment

### VPS/Server Requirements

**Minimum:**
- CPU: 1 core
- RAM: 512 MB
- Storage: 5 GB

**Recommended:**
- CPU: 2 cores
- RAM: 2 GB
- Storage: 20 GB

---

## 🧪 Testing

```bash
# Barcha testlar
pytest

# Coverage bilan
pytest --cov=bot
```

---

## 🐛 Troubleshooting

```bash
# Service statusini tekshirish
sudo systemctl status premiumhubbot

# Loglarni ko'rish
journalctl -u premiumhubbot -f
```

---

## 📝 License

MIT License

---

<div align="center">
  <b>⭐ Agar loyiha yoqsa, star bering!</b>
</div>
