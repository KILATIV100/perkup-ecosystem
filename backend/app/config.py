from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PerkUP"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str
    
    # Redis (Optional для MVP)
    REDIS_URL: Optional[str] = None
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    
    # JWT
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 30
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # Settings
    CHECKIN_COOLDOWN_HOURS: int = 12
    CHECKIN_RADIUS_METERS: int = 100
    POINTS_PER_CHECKIN: int = 1
    
    model_config = {
        "extra": "ignore",  # Ігноруємо зайві поля з .env
        "env_file": ".env",
        "case_sensitive": False  # Не чутливий до регістру
    }

settings = Settings()