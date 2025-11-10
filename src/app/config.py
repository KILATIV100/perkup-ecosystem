# src/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os 

class Settings(BaseSettings):
    """
    Основний клас налаштувань для проєкту PerkUP, оптимізований для Railway.
    Налаштування завантажуються виключно зі змінних середовища.
    """

    # Налаштування Telegram Bot
    BOT_TOKEN: str = Field(..., description="Токен Telegram бота")
    ADMIN_ID: int = Field(123456789, description="Telegram ID для адміністратора")

    # --- Налаштування Poster POS API ---
    POSTER_API_BASE_URL: str = "https://api.joinposter.com/api/v3"
    POSTER_ACCESS_TOKEN: str = Field(..., description="API Access Token для авторизації Poster")
    POSTER_ACCOUNT_DOMAIN: str = Field(..., description="Домен вашого Poster акаунта")
    
    POSTER_SPOT_ID: int = Field(1, description="ID точки продажу (Spot ID)")
    POSTER_CASH_DRAWER_ID: int = Field(1, description="ID каси (Cash Drawer ID)")
    
    # --- Налаштування Бази Даних (Railway/Local) ---
    
    # Прямий DATABASE_URL (найкраще для Railway)
    DATABASE_URL: str = Field(
        None, 
        description="Повний рядок підключення до БД (автоматично надається Railway)"
    )

    # Локальні/Fallback змінні (автоматично захоплюють PG* змінні від Railway, якщо DATABASE_URL не встановлений)
    DB_HOST: str = os.getenv('PGHOST', 'localhost')
    DB_PORT: int = int(os.getenv('PGPORT', 5432))
    DB_NAME: str = os.getenv('PGDATABASE', 'perkup_db')
    DB_USER: str = os.getenv('PGUSER', 'perkup_user')
    DB_PASS: str = os.getenv('PGPASSWORD', 'secret_password')


    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """
        Формує асинхронний рядок підключення до бази даних (з 'postgresql+asyncpg://').
        """
        final_url = self.DATABASE_URL
        
        if not final_url:
            final_url = (
                f"postgresql://{self.DB_USER}:{self.DB_PASS}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
            
        if final_url.startswith("postgresql://"):
            return final_url.replace("postgresql://", "postgresql+asyncpg://")
        
        return final_url

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True 
    )

settings = Settings()
