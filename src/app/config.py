# src/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Основний клас налаштувань для проєкту PerkUP.
    Налаштування завантажуються з .env файлу або змінних середовища.
    """

    # Налаштування Telegram Bot
    BOT_TOKEN: str = "YOUR_BOT_TOKEN_HERE"
    ADMIN_ID: int = 123456789  # ID для адміністратора

    # Налаштування Бази Даних (PostgreSQL/SQLAlchemy)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "perkup_db"
    DB_USER: str = "perkup_user"
    DB_PASS: str = "secret_password"

    # Властивість, що формує URL для підключення до бази даних
    @property
    def DATABASE_URL(self) -> str:
        """Повертає рядок підключення до бази даних PostgreSQL (асинхронний)."""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ігноруємо зайві змінні в .env
    )

# Створюємо єдиний екземпляр налаштувань для використання по всьому проєкту
settings = Settings()
