# src/db/seed.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from src.db.models import Location, Category, Product

# --- Початкові дані з вимог користувача ---

LOCATIONS_DATA = [
    {
        "name": "Mark Mall", 
        "address": "Бровари, вул. Незалежності, 10-А",
        "latitude": 50.514794, 
        "longitude": 30.782308,
        "is_active": True
    },
    {
        "name": "Парк 'Приозерний'", 
        "address": "Бровари, біля озера",
        "latitude": 50.501265, 
        "longitude": 30.754011,
        "is_active": True
    },
]

CATEGORIES_DATA = [
    {"name": "☕️ Кава"},
    {"name": "🍵 Чай"},
    {"name": "🥤 Сезонні напої"},
    {"name": "🍰 Їжа та Випічка"},
    {"name": "🥛 Додатки (Молоко, Сиропи)"},
]

# --- Приклад початкових продуктів ---
PRODUCTS_DATA = [
    # Кава
    {"name": "Еспресо", "description": "Класичний", "base_price": 25.00, "category_name": "☕️ Кава"},
    {"name": "Капучино", "description": "З молочною піною", "base_price": 45.00, "category_name": "☕️ Кава"},
    {"name": "Латте", "description": "М'який кавовий напій", "base_price": 50.00, "category_name": "☕️ Кава"},
    # Випічка
    {"name": "Чізкейк", "description": "Нью-Йоркський чізкейк", "base_price": 85.00, "category_name": "🍰 Їжа та Випічка"},
    {"name": "Круасан", "description": "Класичний масляний", "base_price": 35.00, "category_name": "🍰 Їжа та Випічка"},
]

async def seed_db(session: AsyncSession):
    """
    Наповнює базу даних початковими даними (локації, категорії, продукти),
    якщо вони ще не існують.
    """
    logger.info("Attempting to seed database with initial data...")

    # 1. Створення Локацій
    existing_locations_count = await session.scalar(select(func.count()).select_from(Location))
    if existing_locations_count == 0:
        session.add_all([Location(**data) for data in LOCATIONS_DATA])
        await session.flush()
        logger.success(f"Added {len(LOCATIONS_DATA)} initial locations.")
    else:
        logger.info("Locations already exist. Skipping.")

    # 2. Створення Категорій
    existing_categories_count = await session.scalar(select(func.count()).select_from(Category))
    if existing_categories_count == 0:
        session.add_all([Category(**data) for data in CATEGORIES_DATA])
        await session.flush()
        logger.success(f"Added {len(CATEGORIES_DATA)} initial categories.")
    else:
        logger.info("Categories already exist. Skipping.")
    
    # Отримання ID категорій для продуктів
    categories_map = {c.name: c.id for c in (await session.execute(select(Category))).scalars().all()}

    # 3. Створення Продуктів (з використанням ID категорій)
    existing_products_count = await session.scalar(select(func.count()).select_from(Product))
    if existing_products_count == 0:
        products_to_add = []
        for data in PRODUCTS_DATA:
            category_name = data.pop("category_name")
            data["category_id"] = categories_map.get(category_name)
            if data["category_id"]:
                 products_to_add.append(Product(**data))
        
        session.add_all(products_to_add)
        await session.flush()
        logger.success(f"Added {len(products_to_add)} initial products.")
    else:
        logger.info("Products already exist. Skipping.")

    # 4. Фіксація змін
    await session.commit()
    logger.success("Database seeding completed.")
