"""Admin handlers."""

from aiogram import Router

from . import menu, stats, broadcast, channel, promocode, users, premium_requests, file_id, join_request, test, chat_id

admin_router = Router(name="admin")

# No middleware - using IsAdmin filter per handler
admin_router.include_router(menu.router)
admin_router.include_router(stats.router)
admin_router.include_router(broadcast.router)
admin_router.include_router(channel.router)
admin_router.include_router(promocode.router)
admin_router.include_router(users.router)
admin_router.include_router(premium_requests.router)
admin_router.include_router(file_id.router)
admin_router.include_router(join_request.router)
admin_router.include_router(test.router)
admin_router.include_router(chat_id.router)

__all__ = ["admin_router"]
