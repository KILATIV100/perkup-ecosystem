# src/bot/keyboards/main_menu.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру головного меню.
    UI/UX: Використовуємо емодзі для візуалізації функціоналу.
    """
    builder = InlineKeyboardBuilder()

    # Основні Функції
    builder.row(
        InlineKeyboardButton(text="💸 Мої Перки", callback_data="show_perks"),
        InlineKeyboardButton(text="🎁 Отримати Перк", callback_data="claim_perk")
    )

    # Навігація/Інформація
    builder.row(
        InlineKeyboardButton(text="⚙️ Налаштування", callback_data="settings"),
        InlineKeyboardButton(text="❓ Допомога/FAQ", callback_data="help")
    )
    
    # Використання 'adjust' для автоматичного розподілу кнопок
    # builder.adjust(2, 2) 

    return builder.as_markup()
