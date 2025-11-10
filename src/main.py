# src/main.py (ОНОВЛЕНО: БЕЗ ЗМІНИ ЛОГІКИ, ЛИШЕ ПІДТРИМАННЯ КОНФІГУ)

import asyncio
from aiogram import Bot, Dispatcher
from loguru import logger

from src.app.config import settings
from src.bot.handlers import start

async def main() -> None:
    """
    Головна асинхронна функція для ініціалізації та запуску бота.
    """
    
    # 1. Ініціалізація Логера (Loguru)
    logger.add("file.log", rotation="10 MB", compression="zip", level="INFO")
    logger.info("Starting PerkUP Ecosystem Bot...")

    # 2. Ініціалізація Bot та Dispatcher
    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    # 3. Реєстрація Роутерів (Обробників)
    dp.include_router(start.router)
    
    # ...
    
    # 4. Запуск Polling
    logger.info("Starting bot polling...")
    # Видаляємо пропущені оновлення, щоб бот не відповідав на старі команди
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
