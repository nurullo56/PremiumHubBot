"""Health check endpoint for Railway/VPS monitoring."""

import logging
from typing import Dict, Any

from bot.database.base import get_db

logger = logging.getLogger(__name__)


async def check_database() -> bool:
    """Check if database is accessible."""
    try:
        async with get_db() as db:
            await db.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        return False


async def check_health() -> Dict[str, Any]:
    """
    Perform health check on all critical components.
    
    Returns:
        dict: Health status of each component
    """
    health = {
        "status": "healthy",
        "checks": {}
    }
    
    db_healthy = await check_database()
    health["checks"]["database"] = {
        "status": "healthy" if db_healthy else "unhealthy"
    }
    
    if not db_healthy:
        health["status"] = "unhealthy"
    
    return health


async def health_check_endpoint():
    """
    Simple health check endpoint for HTTP probes.
    
    Usage with aiohttp:
        from aiohttp import web
        
        async def handle_health(request):
            health = await health_check_endpoint()
            status = 200 if health['status'] == 'healthy' else 503
            return web.json_response(health, status=status)
        
        app = web.Application()
        app.router.add_get('/health', handle_health)
    """
    return await check_health()
