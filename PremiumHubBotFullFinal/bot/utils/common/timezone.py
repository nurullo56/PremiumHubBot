"""Timezone utilities for Uzbekistan (UTC+5)."""

from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

UZBEKISTAN_TZ = timezone(timedelta(hours=5))


def get_uzbek_time() -> datetime:
    return datetime.now(UZBEKISTAN_TZ)


def get_uzbek_datetime() -> str:
    return get_uzbek_time().strftime("%Y-%m-%d %H:%M:%S")


def format_for_display(dt: datetime = None) -> str:
    if dt is None:
        dt = get_uzbek_time()
    
    months_uz = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
        5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
        9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
    }
    
    day = dt.day
    month = months_uz[dt.month]
    year = dt.year
    time_str = dt.strftime("%H:%M")
    
    return f"{day}-{month} {year}, {time_str}"


def parse_uzbek_datetime(date_string: str) -> datetime:
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        return dt.replace(tzinfo=UZBEKISTAN_TZ)
    except Exception as e:
        logger.error(f"❌ Failed to parse datetime: {e}")
        return get_uzbek_time()


def get_time_diff(dt: datetime) -> str:
    now = get_uzbek_time()
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UZBEKISTAN_TZ)
    
    diff = now - dt
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Hozir"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} daqiqa oldin"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} soat oldin"
    else:
        days = int(seconds / 86400)
        return f"{days} kun oldin"


def now() -> datetime:
    return get_uzbek_time()


def now_str() -> str:
    return get_uzbek_datetime()
