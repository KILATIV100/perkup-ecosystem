# src/db/seed.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger
from src.db.models import Location, Category, Product, Option, ProductOptionAssociation

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

# --- Опції та Модифікатори ---
OPTIONS_DATA = [
    # Група: Розмір
    {"name": "Маленький", "extra_cost": 0.00, "option_group": "Розмір"},
    {"name": "Середній", "extra_cost": 5.00, "option_group": "Розмір"},
    {"name": "Великий", "extra_cost": 10.00, "option_group": "Розмір"},
    # Група: Тип Молока
    {"name": "Звичайне молоко", "extra_cost": 0.00, "option_group": "Тип молока"},
    {"name": "Вівсяне молоко", "extra_cost": 15.00, "option_group": "Тип молока"},
    {"name": "Кокосове молоко", "extra_cost": 15.00, "option_group": "Тип молока"},
    # Група: Сироп
    {"name": "Без сиропу", "extra_cost": 0.00, "option_group": "Сироп"},
    {"name": "Карамель", "extra_cost": 10.00, "option_group": "Сироп"},
    {"name": "Ваніль", "extra_cost": 10.00, "option_group": "Сироп"},
]


PRODUCTS_DATA = [
    # Кава (БУДЕ КОНФІГУРОВАНА)
    {"name": "Еспресо", "description": "Класичний", "base_price": 25.00, "category_name": "☕️ Кава"},
    {"name": "Капучино", "description": "З молочною піною", "base_price": 45.00, "category_name": "☕️ Кава"},
    {"name": "Латте", "description": "М'який кавовий напій", "base_price": 50.00, "category_name": "☕️ Кава"},
    # Випічка (НЕ БУДЕ КОНФІГУРОВАНА)
    {"name": "Чізкейк", "description": "Нью-Йоркський чізкейк", "base_price": 85.00, "category_name": "🍰 Їжа та Випічка"},
    {"name": "Круасан", "description": "Класичний масляний", "base_price": 35.00, "category_name": "🍰 Їжа та Випічка"},
]

async def seed_db(session: AsyncSession):
    """
    Наповнює базу даних початковими даними (локації, категорії, продукти, опції та асоціації),
    якщо вони ще не існують.
    """
    logger.info("Attempting to seed database with initial data...")

    # 1. Створення Локацій
    if await session.scalar(select(func.count()).select_from(Location)) == 0:
        session.add_all([Location(**data) for data in LOCATIONS_DATA])
        await session.flush()
        logger.success(f"Added {len(LOCATIONS_DATA)} initial locations.")
    else:
        logger.info("Locations already exist. Skipping.")

    # 2. Створення Категорій
    if await session.scalar(select(func.count()).select_from(Category)) == 0:
        session.add_all([Category(**data) for data in CATEGORIES_DATA])
        await session.flush()
        logger.success(f"Added {len(CATEGORIES_DATA)} initial categories.")
    else:
        logger.info("Categories already exist. Skipping.")
    
    # Отримання ID категорій
    categories_map = {c.name: c.id for c in (await session.execute(select(Category))).scalars().all()}
    
    # 3. Створення Продуктів
    if await session.scalar(select(func.count()).select_from(Product)) == 0:
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
    
    # 4. Створення Опцій
    if await session.scalar(select(func.count()).select_from(Option)) == 0:
        session.add_all([Option(**data) for data in OPTIONS_DATA])
        await session.flush()
        logger.success(f"Added {len(OPTIONS_DATA)} initial options.")
    else:
        logger.info("Options already exist. Skipping.")

    # 5. Створення Асоціацій Продукт-Опція
    products_map = {p.name: p.id for p in (await session.execute(select(Product))).scalars().all()}
    options_map = {o.name: o.id for o in (await session.execute(select(Option))).scalars().all()}

    # Капучино та Латте мають всі опції, окрім "Без сиропу"
    configurable_drinks = ["Капучино", "Латте"]
    options_groups_to_add = [o for o in OPTIONS_DATA] # Додаємо всі опції, включаючи "Без сиропу"
    
    # Перевіряємо, чи вже є асоціації
    if await session.scalar(select(func.count()).select_from(ProductOptionAssociation)) == 0:
        associations_to_add = []
        
        for drink_name in configurable_drinks:
            product_id = products_map.get(drink_name)
            if product_id:
                for option_data in options_groups_to_add:
                    option_id = options_map.get(option_data['name'])
                    if option_id:
                        associations_to_add.append(ProductOptionAssociation(product_id=product_id, option_id=option_id))

        session.add_all(associations_to_add)
        await session.flush()
        logger.success(f"Added {len(associations_to_add)} product-option associations.")
    else:
         logger.info("Product-option associations already exist. Skipping.")
             
    await session.commit()
    logger.success("Database seeding completed.")
