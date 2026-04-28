# bot/handlers/user/__init__.py
"""User handlers."""

from aiogram import Router

from . import start, profile, premium_prices, top_rating, promocode, bonus, contact, stars, inline_share, guide, balance_spending
from bot.handlers.registration import registration_router

user_router = Router(name="user")

user_router.include_router(start.router)
user_router.include_router(top_rating.router)
user_router.include_router(profile.router)
user_router.include_router(premium_prices.router)
user_router.include_router(promocode.router)
user_router.include_router(bonus.router)      # ✅
user_router.include_router(contact.router)    # ✅
user_router.include_router(stars.router)      # ✅
user_router.include_router(inline_share.router)  # ✅
user_router.include_router(guide.router)     # ✅
user_router.include_router(balance_spending.router)  # ✅

# ✅ Registration handlerlar (captcha, gender, phone, subscription)
user_router.include_router(registration_router)

__all__ = ["user_router"]