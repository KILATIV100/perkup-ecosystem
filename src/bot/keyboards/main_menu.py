# src/bot/keyboards/main_menu.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру головного меню.
    """
    builder = InlineKeyboardBuilder()

    # Основні Функції
    # Кнопка "Зробити Замовлення" ініціює новий процес (callback: 'start_order')
    builder.row(
        InlineKeyboardButton(text="☕️ Зробити Замовлення", callback_data="start_order")
    )

    # Функціонал Лояльності та Профілю
    builder.row(
        InlineKeyboardButton(text="💸 Мої Бонуси / Профіль", callback_data="show_profile"),
        InlineKeyboardButton(text="⭐ Улюблені Замовлення", callback_data="show_favorites")
    )
    
    # Інформаційний Функціонал
    builder.row(
        InlineKeyboardButton(text="🗺️ Наші Локації", callback_data="show_locations"),
        InlineKeyboardButton(text="💡 Новини та Акції", callback_data="show_news")
    )
    
    builder.adjust(1, 2, 2) 

    return builder.as_markup()
