"""Phone number validation and normalization."""

import re
from typing import Tuple

from bot.config.constants import PHONE_PATTERN


def validate_phone(phone: str) -> Tuple[bool, str]:
    if not phone:
        return False, "Telefon raqami kiritilmagan"
    
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    
    if not re.match(PHONE_PATTERN, phone_clean):
        return False, "Telefon raqami noto'g'ri formatda (+998XXXXXXXXX)"
    
    return True, "OK"


def normalize_phone(phone: str) -> str:
    if not phone:
        return ""
    
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 9:
        return f"+998{digits}"
    elif len(digits) == 12 and digits.startswith('998'):
        return f"+{digits}"
    elif len(digits) == 13 and digits.startswith('998'):
        return f"+{digits}"
    else:
        return phone
