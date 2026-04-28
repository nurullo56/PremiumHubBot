# 💾 Database Schema Documentation

Complete database schema for PremiumHubBot

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tables](#tables)
- [Relationships](#relationships)
- [Indexes](#indexes)
- [Migrations](#migrations)

---

## Overview

**Database:** SQLite 3.x  
**Driver:** aiosqlite (async)  
**Location:** `bot/database.db`  
**Backup:** Auto backup every 24 hours to `backups/`

---

## Tables

### 1. `users` — Foydalanuvchilar

Barcha bot foydalanuvchilarining asosiy ma'lumotlari.

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT,
    phone TEXT,
    gender TEXT CHECK(gender IN ('male', 'female')),
    language_code TEXT DEFAULT 'uz',
    is_premium INTEGER DEFAULT 0,
    is_blocked INTEGER DEFAULT 0,
    is_subscribed INTEGER DEFAULT 0,
    captcha_verified INTEGER DEFAULT 0,
    referred_by INTEGER,
    referral_bonus_given INTEGER DEFAULT 0,
    referral_count INTEGER DEFAULT 0,
    registration_date TEXT NOT NULL,
    last_activity TEXT,
    FOREIGN KEY (referred_by) REFERENCES users(user_id)
);
```

**Columns:**
- `user_id` — Telegram user ID (PK)
- `username` — @username
- `first_name` — Ism
- `last_name` — Familiya
- `phone` — Telefon raqam
- `gender` — Jins (male/female)
- `language_code` — Til kodi (uz/ru/en)
- `is_premium` — Premium user (1/0)
- `is_blocked` — Bloklangan (1/0)
- `is_subscribed` — Kanallarga obuna (1/0)
- `captcha_verified` — Captcha o'tgan (1/0)
- `referred_by` — Kim taklif qilgan (user_id)
- `referral_bonus_given` — Referral bonus berilgan (1/0)
- `referral_count` — Referrallar soni
- `registration_date` — Ro'yxatdan o'tgan sana
- `last_activity` — Oxirgi faollik

---

### 2. `balance` — Balans

Foydalanuvchilarning olmos balansi.

```sql
CREATE TABLE balance (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0.0 CHECK(balance >= 0),
    total_earned REAL DEFAULT 0.0,
    total_spent REAL DEFAULT 0.0,
    last_updated TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**Columns:**
- `user_id` — User ID (PK, FK)
- `balance` — Joriy balans (olmoslar)
- `total_earned` — Jami topilgan
- `total_spent` — Jami sarflangan
- `last_updated` — Oxirgi yangilanish

---

### 3. `premium` — Premium obunalar

Telegram Premium obunalari tarixi.

```sql
CREATE TABLE premium (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    premium_type TEXT DEFAULT 'monthly',
    stars_cost INTEGER DEFAULT 0,
    duration_days INTEGER DEFAULT 30,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    purchased_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**Columns:**
- `id` — Premium record ID (PK)
- `user_id` — User ID (FK)
- `premium_type` — Tur (monthly/yearly)
- `stars_cost` — Narx (Telegram Stars)
- `duration_days` — Davomiyligi (kunlar)
- `start_date` — Boshlanish sanasi
- `end_date` — Tugash sanasi
- `is_active` — Aktiv (1/0)
- `purchased_date` — Sotib olingan sana

---

### 4. `transactions` — Tranzaksiyalar

Balans o'zgarishlarining tarixi.

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    transaction_type TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**Columns:**
- `id` — Transaction ID (PK)
- `user_id` — User ID (FK)
- `amount` — Summa (musbat/manfiy)
- `transaction_type` — Tur (referral_bonus, premium_purchase, etc.)
- `description` — Tavsif
- `created_at` — Yaratilgan sana

**Transaction Types:**
- `referral_bonus` — Referral bonus olish
- `premium_purchase` — Premium sotib olish
- `promocode_bonus` — Promocode bonus
- `admin_adjustment` — Admin tomonidan o'zgartirish

---

### 5. `channels` — Kanallar

Majburiy obuna kanallari.

```sql
CREATE TABLE channels (
    channel_id TEXT PRIMARY KEY,
    channel_name TEXT NOT NULL,
    channel_url TEXT,
    is_active INTEGER DEFAULT 1,
    added_date TEXT NOT NULL,
    added_by INTEGER,
    FOREIGN KEY (added_by) REFERENCES users(user_id)
);
```

**Columns:**
- `channel_id` — Channel ID/username (PK)
- `channel_name` — Kanal nomi
- `channel_url` — Kanal URL
- `is_active` — Aktiv (1/0)
- `added_date` — Qo'shilgan sana
- `added_by` — Kim qo'shgan (admin user_id)

---

### 6. `managed_chats` — Boshqariladigan chatlar

Zayavka kanallari (join request chats).

```sql
CREATE TABLE managed_chats (
    chat_id TEXT PRIMARY KEY,
    fullname TEXT NOT NULL,
    chat_type TEXT DEFAULT 'zayavka',
    invite_link TEXT,
    is_active INTEGER DEFAULT 1,
    added_date TEXT NOT NULL,
    added_by INTEGER,
    description TEXT,
    FOREIGN KEY (added_by) REFERENCES users(user_id)
);
```

**Columns:**
- `chat_id` — Chat ID (PK)
- `fullname` — Chat nomi
- `chat_type` — Tur (zayavka/umumiy/group)
- `invite_link` — Taklif linki
- `is_active` — Aktiv (1/0)
- `added_date` — Qo'shilgan sana
- `added_by` — Kim qo'shgan
- `description` — Tavsif

---

### 7. `join_requests` — Join so'rovlar

Kanal join requestlari tarixi.

```sql
CREATE TABLE join_requests (
    user_id INTEGER NOT NULL,
    chat_id TEXT NOT NULL,
    has_requested INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',
    request_date TEXT,
    approved_date TEXT,
    rejected_date TEXT,
    processed_by INTEGER,
    processed_date TEXT,
    PRIMARY KEY (user_id, chat_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (chat_id) REFERENCES managed_chats(chat_id),
    FOREIGN KEY (processed_by) REFERENCES users(user_id)
);
```

**Columns:**
- `user_id` — User ID (PK)
- `chat_id` — Chat ID (PK)
- `has_requested` — So'rov yuborilgan (1/0)
- `status` — Holat (pending/approved/rejected)
- `request_date` — So'rov sanasi
- `approved_date` — Tasdiqlangan sana
- `rejected_date` — Rad etilgan sana
- `processed_by` — Kim qayta ishlagan
- `processed_date` — Qayta ishlangan sana

---

### 8. `promocodes` — Promokodlar

Bonus promokodlar.

```sql
CREATE TABLE promocodes (
    code TEXT PRIMARY KEY,
    bonus_amount REAL NOT NULL,
    max_uses INTEGER DEFAULT 0,
    current_uses INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_date TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    expire_date TEXT,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);
```

**Columns:**
- `code` — Promocode (PK)
- `bonus_amount` — Bonus miqdori
- `max_uses` — Maksimal foydalanish (0=unlimited)
- `current_uses` — Hozirgi foydalanish
- `is_active` — Aktiv (1/0)
- `created_date` — Yaratilgan sana
- `created_by` — Kim yaratgan
- `expire_date` — Amal qilish muddati

---

### 9. `promocode_usage` — Promocode foydalanish

Promokod foydalanish tarixi.

```sql
CREATE TABLE promocode_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    used_date TEXT NOT NULL,
    bonus_amount REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (code) REFERENCES promocodes(code)
);
```

---

### 10. `fraud_log` — Fraud loglar

Shubhali faoliyat loglari.

```sql
CREATE TABLE fraud_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    fraud_type TEXT NOT NULL,
    description TEXT,
    detected_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

---

## Relationships

```
users (1) ──┬─── (N) balance
            ├─── (N) premium
            ├─── (N) transactions
            ├─── (N) promocode_usage
            ├─── (N) fraud_log
            └─── (N) join_requests

channels (1) ──── (N) [subscription checks]

managed_chats (1) ──── (N) join_requests

promocodes (1) ──── (N) promocode_usage
```

---

## Indexes

```sql
-- Users indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_referred_by ON users(referred_by);
CREATE INDEX idx_users_registration_date ON users(registration_date);

-- Premium indexes
CREATE INDEX idx_premium_user_id ON premium(user_id);
CREATE INDEX idx_premium_active ON premium(is_active);
CREATE INDEX idx_premium_end_date ON premium(end_date);

-- Transactions indexes
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_date ON transactions(created_at);

-- Join requests indexes
CREATE INDEX idx_join_requests_status ON join_requests(status);
CREATE INDEX idx_join_requests_chat ON join_requests(chat_id);
```

---

## Migrations

### Version 1.0 (Initial)

```sql
-- Initial schema creation
-- See: bot/database/migrations.py
```

### Future Migrations

Yangi migration qo'shish:

```python
# bot/database/migrations.py

async def migrate_v2(db):
    """Add new column example."""
    await db.execute("""
        ALTER TABLE users 
        ADD COLUMN new_field TEXT
    """)
    await db.commit()
```

---

## Backup Strategy

- **Auto Backup:** Har 24 soatda
- **Location:** `backups/backup_YYYY-MM-DD_HH-MM-SS.db`
- **Retention:** 30 kun
- **Manual Backup:**

```bash
cp bot/database.db backups/manual_backup_$(date +%Y%m%d).db
```

---

## Optimization

```sql
-- Vacuum (compact database)
VACUUM;

-- Analyze (update statistics)
ANALYZE;

-- Integrity check
PRAGMA integrity_check;
```

---

## Useful Queries

### User Statistics

```sql
SELECT 
    COUNT(*) as total_users,
    SUM(is_premium) as premium_users,
    SUM(is_blocked) as blocked_users,
    SUM(CASE WHEN referral_count >= 40 THEN 1 ELSE 0 END) as eligible_for_premium
FROM users;
```

### Balance Statistics

```sql
SELECT 
    COUNT(*) as users_with_balance,
    SUM(balance) as total_balance,
    AVG(balance) as avg_balance,
    MAX(balance) as max_balance
FROM balance
WHERE balance > 0;
```

### Top Referrers

```sql
SELECT 
    user_id,
    first_name,
    username,
    referral_count
FROM users
WHERE referral_count > 0
ORDER BY referral_count DESC
LIMIT 10;
```

---

<div align="center">
  <b>📊 Database Schema v1.0</b>
</div>
