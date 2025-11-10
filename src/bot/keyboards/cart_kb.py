# src/bot/keyboards/cart_kb.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_cart_keyboard() -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру для керування кошиком.
    """
    builder = InlineKeyboardBuilder()

    # Кнопки для дій у кошику (наразі лише заглушки)
    # TODO: Реалізувати логіку редагування/видалення позицій
    # builder.row(
    #     InlineKeyboardButton(text="✏️ Редагувати позицію", callback_data="edit_item"),
    #     InlineKeyboardButton(text="❌ Очистити кошик", callback_data="clear_cart")
    # )

    # Головні кнопки: Оформити або Продовжити покупки
    builder.row(
        InlineKeyboardButton(text="✅ Оформити Замовлення", callback_data="start_checkout"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Продовжити покупки", callback_data="back_to_menu")
    )
    
    builder.adjust(1, 1)

    return builder.as_markup()
