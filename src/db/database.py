# src/db/database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.app.config import settings

# Створюємо асинхронний двигун (Engine) для PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Встановіть True для детального логування SQL (корисно для відладки)
)

# Створюємо фабрику асинхронних сесій
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, 
)

async def create_db_and_tables(base_class):
    """
    Створює всі таблиці. Використовується для початкового налаштування. 
    У продакшені рекомендується Alembic (система міграцій).
    """
    async with engine.begin() as conn:
        await conn.run_sync(base_class.metadata.create_all)

# Функція для отримання сесії (буде використовуватися для Dependency Injection)
async def get_db_session() -> AsyncSession:
    """Генератор, який надає асинхронну сесію до БД."""
    async with AsyncSessionLocal() as session:
        yield session
