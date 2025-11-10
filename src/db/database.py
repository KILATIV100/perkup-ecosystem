# src/db/database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.app.config import settings

# Створюємо асинхронний двигун (Engine) для PostgreSQL
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL, # <--- ВИКОРИСТОВУЄМО ОНОВЛЕНИЙ URL
    echo=False,  
)

# Створюємо фабрику асинхронних сесій
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, 
)

async def create_db_and_tables(base_class):
    """
    Створює всі таблиці. 
    """
    async with engine.begin() as conn:
        await conn.run_sync(base_class.metadata.create_all)

# Функція для отримання сесії
async def get_db_session() -> AsyncSession:
    """Генератор, який надає асинхронну сесію до БД."""
    async with AsyncSessionLocal() as session:
        yield session
