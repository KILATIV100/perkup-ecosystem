# src/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Основний клас налаштувань для проєкту PerkUP.
    Налаштування завантажуються виключно зі змінних середовища.
    """

    # Налаштування Telegram Bot
    BOT_TOKEN: str
    ADMIN_ID: int = Field(123456789, description="Telegram ID для адміністратора")

    # Налаштування Бази Даних (PostgreSQL/SQLAlchemy)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "perkup_db"
    DB_USER: str = "perkup_user"
    DB_PASS: str = "secret_password"

    # --- НОВІ НАЛАШТУВАННЯ: Poster POS API ---
    POSTER_API_BASE_URL: str = "https://api.joinposter.com/api/v3"
    POSTER_ACCESS_TOKEN: str = Field(..., description="API Access Token для авторизації")
    POSTER_ACCOUNT_DOMAIN: str = Field(..., description="Домен вашого Poster акаунта (напр., perkup)")
    
    # ID вашого закладу/каси для створення замовлення
    POSTER_SPOT_ID: int = Field(1, description="ID точки продажу (Spot ID) для замовлень")
    POSTER_CASH_DRAWER_ID: int = Field(1, description="ID каси (Cash Drawer ID)")


    @property
    def DATABASE_URL(self) -> str:
        """Повертає рядок підключення до бази даних PostgreSQL (асинхронний)."""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Створюємо єдиний екземпляр налаштувань
settings = Settings()
