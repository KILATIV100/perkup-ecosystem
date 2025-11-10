# src/main.py

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from loguru import logger
import httpx 

# --- Імпорти з нашої екосистеми ---
from src.app.config import settings
from src.db.models import Base
from src.db.database import create_db_and_tables, AsyncSessionLocal
from src.db.seed import seed_db
from src.app.repositories.user_repo import UserRepository
from src.app.repositories.location_repo import LocationRepository
from src.app.repositories.product_repo import ProductRepository 
from src.app.repositories.order_repo import OrderRepository
from src.db.database import get_db_session
from src.app.services.loyalty_service import PosterLoyaltyService 

# --- Ініціалізація Сервісів ---
try:
    loyalty_service = PosterLoyaltyService()
except Exception as e:
    logger.error(f"Failed to initialize PosterLoyaltyService: {e}")
    loyalty_service = None 

# --- Middlewares ---

async def db_session_middleware(handler, event: Update, data: dict):
    """
    Middleware, який ініціалізує сесію бази даних для кожного запиту
    та передає об'єкти Repository у хендлер (Dependency Injection).
    """
    
    async for session in get_db_session():
        # 1. Ініціалізація Репозиторіїв
        user_repo = UserRepository(session)
        location_repo = LocationRepository(session)
        product_repo = ProductRepository(session)
        order_repo = OrderRepository(session)
        
        # 2. Передача в контекст
        data["session"] = session
        data["user_repo"] = user_repo
        data["location_repo"] = location_repo
        data["product_repo"] = product_repo 
        data["order_repo"] = order_repo
        data["loyalty_service"] = loyalty_service
        
        # 3. Виконання наступного хендлера/мідлвару
        result = await handler(event, data)
        
        return result


async def main() -> None:
    """
    Головна асинхронна функція для ініціалізації та запуску бота.
    """
    
    # 1. Ініціалізація Логера
    logger.add("file.log", rotation="10 MB", compression="zip", level="INFO")
    logger.info("Starting PerkUP Ecosystem Bot...")
    
    if loyalty_service is None:
        logger.error("PosterLoyaltyService is NOT initialized. Loyalty functions will fail.")

    # 2. Ініціалізація Бази Даних та Таблиць
    logger.info(f"Connecting to database: {settings.DB_HOST}/{settings.DB_NAME}...")
    await create_db_and_tables(Base) 
    logger.success("Database tables initialized successfully (or already exist).")
    
    # 3. Наповнення Бази Даних Початковими Даними (Seeding)
    async with AsyncSessionLocal() as session:
        await seed_db(session)
    logger.success("Database seeding completed.")


    # 4. Ініціалізація Bot та Dispatcher
    from src.bot.handlers import start, menu, profile # <--- ДОДАНО PROFILE
    
    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    # 5. Реєстрація Роутерів (Обробників)
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(profile.router) # <--- РЕЄСТРАЦІЯ PROFILE
    
    # 6. Встановлення Middleware для Dependency Injection
    dp.update.middleware(db_session_middleware)
    
    # 7. Запуск Polling
    logger.info("Starting bot polling...")
    await bot.delete_webhook(drop_pending_updates=True) 
    
    if loyalty_service and loyalty_service._client:
        dp.shutdown.register(loyalty_service._client.aclose)
        
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        import httpx
    except ImportError:
        print("ERROR: Бібліотека 'httpx' не встановлена. Додайте 'httpx' до requirements.txt і встановіть її.")
        exit(1)
        
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot stopped by user or system signal.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
