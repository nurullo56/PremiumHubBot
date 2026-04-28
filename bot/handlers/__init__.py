# bot/handlers/__init__.py
"""Handlers package."""

from aiogram import Router

from .user import user_router
from .premium import referral_router
from .admin import admin_router
from . import channel_monitor
from . import join_request


def get_main_router() -> Router:
    """Get main router with all sub-routers."""
    router = Router()
    
    router.include_router(user_router)
    router.include_router(referral_router)
    router.include_router(admin_router)
    router.include_router(channel_monitor.router)
    router.include_router(join_request.router)
    
    return router


__all__ = ["get_main_router", "user_router", "admin_router", "referral_router"]