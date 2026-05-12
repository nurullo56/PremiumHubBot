"""Premium handlers."""

from aiogram import Router
from . import referral

referral_router = Router(name="premium")
referral_router.include_router(referral.router)

__all__ = ["referral_router"]