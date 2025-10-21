from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "PerkUP"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    
    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 30
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # Settings
    CHECKIN_COOLDOWN_HOURS: int = 12
    CHECKIN_RADIUS_METERS: int = 100
    POINTS_PER_CHECKIN: int = 1
    
    class Config:
        env_file = ".env"

settings = Settings()