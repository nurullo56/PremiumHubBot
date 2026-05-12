# 📘 API Reference

Complete API reference for PremiumHubBot services and repositories.

---

## 📋 Table of Contents

- [Repositories](#repositories)
- [Services](#services)
- [Utilities](#utilities)
- [Filters](#filters)

---

## Repositories

Repository layer — database access abstraction.

### UserRepository

**Location:** `bot/database/repositories/user_repo.py`

#### Methods

##### `create(user_id, first_name, **kwargs)`

Create new user.

```python
success = await user_repo.create(
    user_id=123456,
    first_name="John",
    username="john_doe",
    phone="+998901234567",
    gender="male"
)
```

**Parameters:**
- `user_id` (int) — Telegram user ID
- `first_name` (str) — User first name
- `**kwargs` — Additional fields

**Returns:** `bool` — Success status

---

##### `get_by_id(user_id)`

Get user by ID.

```python
user = await user_repo.get_by_id(123456)
# Returns: Dict or None
```

**Returns:** `Optional[Dict]` — User data

---

##### `update(user_id, data)`

Update user data.

```python
success = await user_repo.update(
    user_id=123456,
    data={'phone': '+998901234567'}
)
```

**Parameters:**
- `user_id` (int) — User ID
- `data` (dict) — Fields to update

**Returns:** `bool`

---

##### `update_subscription(user_id, is_subscribed)`

Update subscription status.

```python
await user_repo.update_subscription(123456, True)
```

---

### BalanceRepository

**Location:** `bot/database/repositories/balance_repo.py`

#### Methods

##### `get_balance(user_id)`

Get user balance.

```python
balance = await balance_repo.get_balance(123456)
# Returns: Decimal('10.5')
```

**Returns:** `Decimal` — Current balance

---

##### `add_balance(user_id, amount, description)`

Add to balance (with transaction log).

```python
success, new_balance = await balance_repo.add_balance(
    user_id=123456,
    amount=Decimal('1.4'),
    description="Referral bonus"
)
```

**Returns:** `tuple[bool, Decimal]` — (success, new_balance)

---

##### `deduct_balance(user_id, amount, description)`

Deduct from balance.

```python
success, new_balance = await balance_repo.deduct_balance(
    user_id=123456,
    amount=Decimal('56'),
    description="Premium purchase"
)
```

**Returns:** `tuple[bool, Decimal]`

---

##### `set_balance(user_id, amount)`

Set exact balance (admin only).

```python
success = await balance_repo.set_balance(123456, Decimal('100'))
```

**Returns:** `bool`

---

### ReferralBonusRepository

**Location:** `bot/database/repositories/referral_bonus_repo.py`

#### Functions

##### `give_referral_bonus(referrer_id, referee_id, referee_name, bot)`

Give referral bonus.

```python
success, msg = await give_referral_bonus(
    referrer_id=123456,
    referee_id=789012,
    referee_name="John Doe",
    bot=bot
)
```

**Parameters:**
- `referrer_id` (int) — Referrer user ID
- `referee_id` (int) — New user ID
- `referee_name` (str) — New user name
- `bot` (Bot) — Bot instance

**Returns:** `tuple[bool, str]` — (success, message)

---

##### `get_active_referrals_count(user_id)`

Get count of active referrals.

```python
count = await get_active_referrals_count(123456)
# Returns: int
```

---

### PremiumRepository

**Location:** `bot/database/repositories/premium_repo.py`

#### Methods

##### `create_premium(user_id, premium_type, duration_days, stars_cost)`

Create premium record.

```python
success = await premium_repo.create_premium(
    user_id=123456,
    premium_type='monthly',
    duration_days=30,
    stars_cost=0
)
```

---

##### `get_active_premium(user_id)`

Get active premium status.

```python
premium = await premium_repo.get_active_premium(123456)
# Returns: Dict or None
```

---

##### `deactivate_expired_premiums()`

Deactivate expired premiums (cron job).

```python
count = await premium_repo.deactivate_expired_premiums()
# Returns: int (count of deactivated)
```

---

## Services

Service layer — business logic.

### SubscriptionChecker

**Location:** `bot/utils/subscription_checker.py`

#### Methods

##### `get_all_mandatory_channels()`

Get all mandatory channels.

```python
channels = await subscription_checker.get_all_mandatory_channels()
# Returns: List[Dict]
# [
#   {
#     'channel_id': '@channel',
#     'channel_name': 'Channel Name',
#     'channel_url': 'https://t.me/channel',
#     'type': 'public'
#   }
# ]
```

---

##### `check_user_subscriptions(bot, user_id)`

Check if user subscribed to all channels.

```python
is_subscribed = await subscription_checker.check_user_subscriptions(
    bot=bot,
    user_id=123456
)
# Returns: bool
```

---

##### `get_subscription_keyboard(bot, user_id)`

Get subscription keyboard.

```python
keyboard = await subscription_checker.get_subscription_keyboard(
    bot=bot,
    user_id=123456
)
# Returns: Optional[InlineKeyboardMarkup]
```

---

##### `get_unsubscribed_channels(bot, user_id)`

Get list of unsubscribed channels.

```python
channels = await subscription_checker.get_unsubscribed_channels(
    bot=bot,
    user_id=123456
)
# Returns: List[Dict]
```

---

### ReferralService

**Location:** `bot/services/referral/referral_service.py`

#### Methods

##### `get_status(user_id)`

Get referral status.

```python
status = await referral_service.get_status(123456)
# Returns: {
#   'count': 15,
#   'link': 'https://t.me/bot?start=123456',
#   'remaining': 25,
#   'percent': 37
# }
```

---

## Utilities

### Bot Instance

**Location:** `bot/utils/bot/instance.py`

#### Usage

```python
from bot.utils.bot.instance import BotInstance

# Set bot instance (in main.py)
BotInstance.set(bot)

# Get bot instance anywhere
bot = BotInstance.get()
```

---

## Filters

### IsAdmin

**Location:** `bot/filters/admin.py`

Custom filter for admin-only handlers.

#### Usage

```python
from bot.filters import IsAdmin

@router.message(IsAdmin(), F.text == "📊 Statistika")
async def stats_handler(message: Message):
    # Only accessible by admins
    pass
```

---

## Examples

### Complete User Registration Flow

```python
from bot.database.repositories.user_repo import user_repo
from bot.database.repositories.balance_repo import balance_repo
from bot.utils.subscription_checker import subscription_checker

async def register_user(user_id, first_name, referred_by=None):
    # 1. Create user
    success = await user_repo.create(
        user_id=user_id,
        first_name=first_name,
        referred_by=referred_by
    )
    
    # 2. Initialize balance
    if success:
        await balance_repo.create(user_id)
    
    # 3. Check subscriptions
    is_subscribed = await subscription_checker.check_user_subscriptions(
        bot=bot,
        user_id=user_id
    )
    
    return success and is_subscribed
```

### Give Referral Bonus

```python
from bot.database.repositories.referral_bonus_repo import give_referral_bonus

async def process_referral(referrer_id, referee_id, referee_name, bot):
    success, msg = await give_referral_bonus(
        referrer_id=referrer_id,
        referee_id=referee_id,
        referee_name=referee_name,
        bot=bot
    )
    
    if success:
        print(f"✅ Bonus given: {msg}")
    else:
        print(f"❌ Failed: {msg}")
```

### Check Premium Eligibility

```python
from bot.database.repositories.referral_bonus_repo import get_active_referrals_count
from bot.config import settings

async def can_get_premium(user_id):
    count = await get_active_referrals_count(user_id)
    return count >= settings.required_referrals
```

---

<div align="center">
  <b>📖 API Reference v1.0</b>
</div>
