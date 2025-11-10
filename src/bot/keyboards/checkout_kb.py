# src/bot/keyboards/checkout_kb.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

def get_pickup_time_keyboard() -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру для вибору часу отримання замовлення.
    """
    builder = InlineKeyboardBuilder()
    
    # 1. Замовлення "Зараз"
    builder.row(
        InlineKeyboardButton(text="⚡️ Якнайшвидше (Зараз)", callback_data="time:now")
    )
    
    # 2. Замовлення на певний час (інтервали)
    now = datetime.now()
    times = [10, 20, 30] # Хвилини від поточного часу
    
    for minutes in times:
        future_time = now + timedelta(minutes=minutes)
        time_str = future_time.strftime("%H:%M")
        
        builder.button(
            text=f"На {time_str} (+{minutes} хв)",
            callback_data=f"time:{minutes}"
        )
    
    builder.adjust(1, 2, 1)

    # 3. Навігаційні кнопки
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад до Кошика", callback_data="show_cart")
    )

    return builder.as_markup()

def get_payment_method_keyboard(total_amount: float, available_points: int) -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру для вибору способу оплати.
    :param available_points: Кількість доступних бонусних балів.
    """
    builder = InlineKeyboardBuilder()

    # Онлайн Оплата (Критично важливо для швидких замовлень)
    builder.row(
        InlineKeyboardButton(text="💳 Оплатити Онлайн (LiqPay/MonoPay)", callback_data="pay:online")
    )

    # Оплата при отриманні
    builder.row(
        InlineKeyboardButton(text="💰 Оплата готівкою/карткою при отриманні", callback_data="pay:upon_pickup")
    )
    
    # Використання бонусів (відображається, якщо є доступні бали)
    if available_points > 0:
        # Припустимо, 1 бонус = 1 гривня. Не більше 50% чека.
        max_spend = int(total_amount * 0.5)
        points_to_spend = min(available_points, max_spend)
        
        builder.row(
            InlineKeyboardButton(
                text=f"✨ Сплатити {points_to_spend} бонусами ({points_to_spend:.2f} грн)", 
                callback_data=f"pay:bonus:{points_to_spend}"
            )
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад до Часу Отримання", callback_data="back_to_time_select")
    )

    return builder.as_markup()
