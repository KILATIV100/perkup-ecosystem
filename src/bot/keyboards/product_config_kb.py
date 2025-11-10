# src/bot/keyboards/product_config_kb.py

from typing import List, Dict
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.app.domain.models import ConfigurableProductDTO, OptionDTO
from src.app.utils.cart_utils import calculate_item_price

def get_product_config_keyboard(
    product: ConfigurableProductDTO, 
    selected_ids: List[int], 
    quantity: int = 1
) -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру для конфігурації продукту (вибір опцій та кількості).
    """
    builder = InlineKeyboardBuilder()

    # 1. Групування опцій
    grouped_options: Dict[str, List[OptionDTO]] = {}
    for option in product.available_options:
        if option.option_group not in grouped_options:
            grouped_options[option.option_group] = []
        grouped_options[option.option_group].append(option)
    
    # 2. Кнопки для груп опцій
    for group, options in grouped_options.items():
        row_buttons = []
        for option in options:
            is_selected = option.id in selected_ids
            # Якщо опція є частиною групи, яку користувач повинен вибрати (наприклад, Розмір), 
            # і вона не вибрана, то це "🔘". Якщо вибрана, то "✅".
            prefix = "✅ " if is_selected else "🔘 "
            
            # Додаємо вартість, якщо вона є
            cost_suffix = f" (+{option.extra_cost:.2f})" if option.extra_cost > 0 else ""
            
            # Callback data format: 'toggle_opt:OPTION_ID'
            callback_data = f"toggle_opt:{option.id}"
            
            row_buttons.append(
                InlineKeyboardButton(
                    text=f"{prefix}{option.name}{cost_suffix}",
                    callback_data=callback_data
                )
            )
        # Додаємо кнопки групою, щоб вони займали один або два ряди
        builder.row(*row_buttons)

    # 3. Кнопки Кількість та Кошик (завжди внизу)
    current_price, _ = calculate_item_price(product, selected_ids)
    
    # Кнопки для зміни кількості
    builder.row(
        InlineKeyboardButton(text="➖", callback_data="change_qty:-1"),
        InlineKeyboardButton(text=f"Кількість: {quantity}", callback_data="ignore"),
        InlineKeyboardButton(text="➕", callback_data="change_qty:+1")
    )

    # Кнопка фіналізації
    builder.row(
        InlineKeyboardButton(
            text=f"🛒 Додати до кошика ({current_price * quantity:.2f} грн)", 
            callback_data="add_to_cart"
        )
    )
    
    # Кнопка скасування
    builder.row(
        InlineKeyboardButton(text="⬅️ Скасувати", callback_data="back_to_menu")
    )
    
    return builder.as_markup()

def format_config_summary(product: ConfigurableProductDTO, selected_ids: List[int], summary_text: str) -> str:
    """Формує текст повідомлення конфігуратора."""
    current_price, _ = calculate_item_price(product, selected_ids)
    
    # Перевірка: чи вибрана хоча б одна опція з кожної обов'язкової групи (якщо це потрібно)
    
    text = (
        f"🛠️ **Конфігурація: {product.name}**\n\n"
        f"**Базова ціна**: {product.base_price:.2f} грн\n"
        f"**Поточна ціна за одиницю**: {current_price:.2f} грн\n\n"
        f"**Виберіть опції**:\n"
        f"{summary_text}\n"
    )
    return text
