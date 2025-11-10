# src/bot/keyboards/info_kb.py

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.app.domain.models import LocationDTO

# URL для Google Maps
GOOGLE_MAPS_BASE_URL = "https://www.google.com/maps/search/?api=1&query="

def get_locations_keyboard(locations: List[LocationDTO]) -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру зі списком локацій та посиланням на Google Maps.
    """
    builder = InlineKeyboardBuilder()

    for location in locations:
        # Формуємо URL для Google Maps з координатами
        maps_url = f"{GOOGLE_MAPS_BASE_URL}{location.latitude},{location.longitude}"
        
        # Кнопка для відкриття карти
        builder.row(
            InlineKeyboardButton(
                text=f"🗺️ {location.name}",
                url=maps_url
            )
        )
        # Кнопка для відправки Telegram Location (callback)
        builder.row(
            InlineKeyboardButton(
                text="📌 Показати на карті Telegram", 
                callback_data=f"send_loc:{location.id}"
            )
        )
        # Додаємо розділювач, якщо це не остання локація
        builder.row(InlineKeyboardButton(text="—", callback_data="ignore"))

    # Навігація
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад до Головного Меню", callback_data="back_to_main")
    )
    
    builder.adjust(1, 1, 1, 1)

    return builder.as_markup()


def get_news_keyboard() -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру з посиланнями на Новини та Соцмережі.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📢 Наш Telegram-канал (@perkup_news)", url="https://t.me/perkup_news")
    )
    builder.row(
        InlineKeyboardButton(text="📸 Наш Instagram", url="https://instagram.com/perkup") # Умовний URL
    )

    # Кнопка повернення
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад до Головного Меню", callback_data="back_to_main")
    )
    
    return builder.as_markup()
