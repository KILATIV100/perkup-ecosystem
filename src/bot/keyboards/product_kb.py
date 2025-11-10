# src/bot/keyboards/product_kb.py

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.app.domain.models import ProductDTO

def get_products_list_keyboard(products: List[ProductDTO], category_id: int, cart_total: float) -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру зі списком продуктів у вибраній категорії.
    :param products: Список ProductDTO для відображення.
    :param category_id: ID поточної категорії (для кнопки "Назад").
    :param cart_total: Поточна сума кошика для відображення.
    """
    builder = InlineKeyboardBuilder()

    # 1. Додаємо кнопки для кожного продукту
    for product in products:
        # Callback data format: 'select_prod:PRODUCT_ID'
        callback_data = f"select_prod:{product.id}"
        
        # Відображення назви та ціни
        text = f"{product.name} ({product.base_price:.2f} грн)"
        
        builder.button(
            text=text,
            callback_data=callback_data
        )
    
    # 2. Навігаційні кнопки
    builder.row(
        InlineKeyboardButton(text=f"🛒 Кошик ({cart_total:.2f} грн)", callback_data="show_cart"),
    )
    
    # Кнопка "Назад" до категорій. Callback data format: 'back_to_cat:CATEGORY_ID'
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад до Категорій", callback_data="back_to_cat_list")
    )

    # Розподіляємо кнопки по одній у ряд для кращого сприйняття списку
    builder.adjust(1) 
    
    return builder.as_markup()
