# bot/handlers/registration/__init__.py
"""Registration handlers package."""

from aiogram import Router

from . import captcha, gender, phone, subscription

registration_router = Router(name="registration")

registration_router.include_router(captcha.router)
registration_router.include_router(gender.router)
registration_router.include_router(phone.router)
registration_router.include_router(subscription.router)

__all__ = ["registration_router"]