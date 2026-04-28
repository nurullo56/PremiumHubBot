"""Application settings using Pydantic."""

import logging
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===================== BOT =====================
    bot_token: str = Field(..., description="Telegram Bot Token")
    bot_username: str = Field(..., description="Bot username without @")

    # ===================== ADMIN =====================
    admin_id: str = Field(..., description="Admin IDs (comma-separated)")
    admin_username: str = Field(default="", description="Admin username")

    # ===================== FILE IDs =====================
    premium_file_id: str = Field(default="", description="Premium image file ID")
    stars_file_id: str = Field(default="", description="Stars image file ID")
    top_file_id: str = Field(default="", description="Top rating image file ID")
    spend_image_id: str = Field(default="", description="Spend stats image file ID")
    account_image_id: str = Field(default="", description="Account image file ID")

    # ===================== REFERRAL =====================
    required_referrals: int = Field(default=40, description="Required referrals for bonus")

    # ===================== PAGINATION =====================
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")

    # ===================== TEST MODE =====================
    test_mode: bool = Field(default=True, description="Enable test mode")

    # ===================== CAPTCHA =====================
    captcha_web_app_url: str = Field(default="", description="Captcha WebApp URL")

    # ===================== AI =====================
    gemini_api_key: str = Field(default="", description="Google Gemini API Key")

    # ===================== DATABASE =====================
    db_path: str = Field(default="database/bot.db", description="SQLite database path")

    # ===================== MONITORING =====================
    sentry_dsn: str = Field(default="", description="Sentry DSN for error tracking")
    environment: str = Field(default="production", description="Environment name")

    # ===================== CACHE (Future) =====================
    # redis_host: str = Field(default="localhost", description="Redis host")
    # redis_port: int = Field(default=6379, description="Redis port")
    # redis_db: int = Field(default=0, description="Redis database number")

    # ===================== COMPUTED PROPERTIES =====================

    @property
    def admin_ids(self) -> List[int]:
        """Parse admin IDs from comma-separated string."""
        if not self.admin_id:
            return []
        
        try:
            return [
                int(id_str.strip())
                for id_str in self.admin_id.split(",")
                if id_str.strip().isdigit()
            ]
        except (ValueError, AttributeError):
            logger.error(f"Failed to parse admin_id: {self.admin_id}")
            return []

    @property
    def first_admin_id(self) -> int:
        """Get first admin ID."""
        ids = self.admin_ids
        return ids[0] if ids else 0

    @property
    def db_full_path(self) -> Path:
        """Get absolute database path."""
        return Path(self.db_path).absolute()

    @property
    def admin_mention(self) -> str:
        """Get admin mention string."""
        if self.admin_username:
            return f"@{self.admin_username.lstrip('@')}"
        return "admin"

    # ===================== VALIDATORS =====================

    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        """Validate bot token format."""
        # Allow test tokens for testing
        if v.startswith("test_"):
            return v
        
        if not v or v == "your_bot_token_here":
            raise ValueError("BOT_TOKEN must be set in .env file")
        if ":" not in v:
            raise ValueError("Invalid BOT_TOKEN format")
        return v

    @field_validator("admin_id")
    @classmethod
    def validate_admin_id(cls, v: str) -> str:
        """Validate admin ID."""
        if not v:
            raise ValueError("ADMIN_ID must be set in .env file")
        return v

    # ===================== HELPERS =====================

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in self.admin_ids

    def validate_critical_settings(self) -> None:
        """Validate critical settings and log warnings."""
        errors = []
        warnings = []

        # Critical checks
        if not self.bot_token or self.bot_token == "your_bot_token_here":
            errors.append("BOT_TOKEN is not properly configured")

        if not self.bot_username:
            errors.append("BOT_USERNAME is not set")

        if not self.admin_ids:
            errors.append("No valid ADMIN_ID found")

        # Non-critical warnings
        if not self.admin_username:
            warnings.append("ADMIN_USERNAME not set - users won't be able to contact admin")

        if not self.captcha_web_app_url and not self.test_mode:
            warnings.append("CAPTCHA_WEB_APP_URL not set - captcha won't work")

        if not self.gemini_api_key:
            warnings.append("GEMINI_API_KEY not set - AI features disabled")

        if not self.sentry_dsn:
            warnings.append("SENTRY_DSN not set - error tracking disabled")

        # Raise errors
        if errors:
            error_msg = "❌ Critical configuration errors:\n" + "\n".join(f"  • {e}" for e in errors)
            raise RuntimeError(error_msg)

        # Log warnings
        if warnings:
            for warning in warnings:
                logger.warning(f"⚠️ {warning}")


# ===================== SINGLETON INSTANCE =====================

settings = Settings()

# Auto-validate on import
try:
    settings.validate_critical_settings()
    logger.info("✅ Configuration validated successfully")
except RuntimeError as e:
    logger.error(str(e))
    print(str(e))
    print("\n⚠️ Please configure .env file properly!")
    raise