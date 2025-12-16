"""Application configuration settings"""

import json
from typing import List, Any
from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache


DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://perkup.com.ua",
    "https://tma.perkup.com.ua",
]


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "PerkUP"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/perkup"
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 30

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_WEBAPP_URL: str = "https://tma.perkup.com.ua"

    # CORS - stored as str to avoid pydantic-settings JSON parsing issues
    CORS_ORIGINS: str = ""

    @model_validator(mode="before")
    @classmethod
    def preprocess_settings(cls, data: Any) -> Any:
        """Preprocess settings before validation"""
        if isinstance(data, dict):
            # Convert DATABASE_URL to asyncpg format
            db_url = data.get("DATABASE_URL", "")
            if db_url:
                if db_url.startswith("postgresql://"):
                    data["DATABASE_URL"] = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
                elif db_url.startswith("postgres://"):
                    data["DATABASE_URL"] = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        return data

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if not self.CORS_ORIGINS or self.CORS_ORIGINS.strip() == "":
            return DEFAULT_CORS_ORIGINS
        v = self.CORS_ORIGINS.strip()
        # Try JSON array first
        if v.startswith("["):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        # Comma-separated
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    # Check-in settings
    CHECKIN_RADIUS_METERS: int = 100
    CHECKIN_COOLDOWN_HOURS: int = 12

    # Game settings
    GAME_MAX_POINTS_DEFAULT: int = 20
    GAME_POINTS_CONVERSION_RATE: float = 0.02

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
