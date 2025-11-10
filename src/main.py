# src/main.py

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from loguru import logger

# --- Імпорти з нашої екосистеми ---
from src.app.config import settings
from src.bot.handlers import start
from src.db.models import Base
from src.db.database import create_db_and_tables, AsyncSessionLocal
from src.db.seed import seed_db
from src.app.repositories.user_repo import UserRepository
from src.db.database import get_db_session # Імпорт генератора сесій

# --- Middlewares ---

# Тут ми використовуємо простий функціональний підхід для DI,
# який буде додавати сесію та репозиторій до контексту оновлення.
async def db_session_middleware(handler, event: Update, data: dict):
    """
    Middleware, який ініціалізує сесію бази даних для кожного запиту
    та передає об'єкт UserRepository у хендлер.
    """
    
    # 1. Отримання сесії через генератор
    async for session in get_db_session():
        # 2. Ініціалізація Репозиторію
        user_repo = UserRepository(session)
        
        # 3. Передача в контекст
        data["session"] = session
        data["user_repo"] = user_repo
        
        # 4. Виконання наступного хендлера/мідлвару
        result = await handler(event, data)
        
        # 5. Сесія закривається автоматично після виходу з 'async with' у get_db_session
        return result


async def main() -> None:
    """
    Головна асинхронна функція для ініціалізації та запуску бота.
    """
    
    # 1. Ініціалізація Логера
    logger.add("file.log", rotation="10 MB", compression="zip", level="INFO")
    logger.info("Starting PerkUP Ecosystem Bot...")

    # 2. Ініціалізація Бази Даних та Таблиць
    logger.info(f"Connecting to database: {settings.DB_HOST}/{settings.DB_NAME}...")
    await create_db_and_tables(Base) # Створюємо таблиці
    logger.success("Database tables initialized successfully (or already exist).")
    
    # 3. Наповнення Бази Даних Початковими Даними (Seeding)
    async with AsyncSessionLocal() as session:
        await seed_db(session)
    logger.success("Database seeding completed.")


    # 4. Ініціалізація Bot та Dispatcher
    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    # 5. Реєстрація Роутерів (Обробників)
    dp.include_router(start.router)
    
    # 6. Встановлення Middleware для Dependency Injection
    # Всі оновлення тепер будуть мати доступ до 'session' та 'user_repo'
    dp.update.middleware(db_session_middleware)
    
    # 7. Запуск Polling
    logger.info("Starting bot polling...")
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        # Запуск асинхронної функції
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot stopped by user or system signal.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
