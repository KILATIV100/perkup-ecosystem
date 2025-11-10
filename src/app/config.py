# src/app/config.py (ОНОВЛЕНО)

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Основний клас налаштувань для проєкту PerkUP.
    Налаштування завантажуються виключно зі змінних середовища.
    """

    # Налаштування Telegram Bot
    # Зверніть увагу: ці значення повинні бути встановлені як Secrets у Codespaces!
    BOT_TOKEN: str
    ADMIN_ID: int = 123456789  # ID для адміністратора (можна залишити значення за замовчуванням)

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
        # Використовуємо f-рядок для формування URL
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        # Видаляємо env_file=".env". Тепер Pydantic шукає лише в Environment Variables.
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Створюємо єдиний екземпляр налаштувань
settings = Settings()
