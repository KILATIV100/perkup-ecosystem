# src/bot/keyboards/location_menu.py

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.app.domain.models import LocationDTO # Використовуємо DTO, а не ORM-модель

def get_location_selection_keyboard(locations: List[LocationDTO]) -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру для вибору локації з доступного списку.
    UI/UX: Кнопка містить назву локації. Callback-дані містять ID.
    """
    builder = InlineKeyboardBuilder()

    for location in locations:
        # Callback data format: 'select_loc:ID'
        callback_data = f"select_loc:{location.id}"
        builder.button(
            text=f"📍 {location.name}",
            callback_data=callback_data
        )
    
    # Додаємо кнопку, якщо локації не підходять або потрібна допомога
    builder.row(
        InlineKeyboardButton(text="❓ Мої локації відсутні / Допомога", callback_data="help_location")
    )

    # Розподіляємо кнопки по дві в ряд для кращого вигляду
    builder.adjust(2) 
    
    return builder.as_markup()
