# src/bot/keyboards/menu_kb.py

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.app.domain.models import CategoryDTO

def get_category_menu_keyboard(categories: List[CategoryDTO], cart_total: float) -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру для вибору категорії товарів.
    UI/UX: Включає динамічну суму кошика.
    """
    builder = InlineKeyboardBuilder()

    for category in categories:
        # Callback data format: 'select_cat:ID'
        callback_data = f"select_cat:{category.id}"
        builder.button(
            text=category.name,
            callback_data=callback_data
        )
    
    # Кнопки для навігації
    builder.row(
        InlineKeyboardButton(text=f"🛒 Кошик ({cart_total:.2f} грн)", callback_data="show_cart"),
        InlineKeyboardButton(text="⬅️ Назад до Головного Меню", callback_data="back_to_main")
    )

    # Розподіляємо кнопки по дві в ряд
    builder.adjust(2, 2, 1) 
    
    return builder.as_markup()
