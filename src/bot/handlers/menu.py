# src/bot/handlers/menu.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger
from typing import List
from datetime import datetime, timedelta

# --- Репозиторії ---
from src.app.repositories.user_repo import UserRepository
from src.app.repositories.location_repo import LocationRepository
from src.app.repositories.product_repo import ProductRepository
from src.app.repositories.order_repo import OrderRepository # <--- НОВИЙ ІМПОРТ

# --- Клавіатури ---
from src.bot.keyboards.menu_kb import get_category_menu_keyboard
from src.bot.keyboards.main_menu import get_main_menu_keyboard
from src.bot.keyboards.product_kb import get_products_list_keyboard
from src.bot.keyboards.product_config_kb import get_product_config_keyboard, format_config_summary 
from src.bot.keyboards.cart_kb import get_cart_keyboard # <--- НОВИЙ ІМПОРТ
from src.bot.keyboards.checkout_kb import get_pickup_time_keyboard, get_payment_method_keyboard # <--- НОВИЙ ІМПОРТ

# --- Domain/States/Utils ---
from src.app.domain.models import CategoryDTO, ProductDTO, ShoppingCartDTO, ConfigurableProductDTO, CartItemDTO, OptionDTO
from src.bot.states.order import OrderState
from src.app.utils.cart_utils import calculate_item_price, get_selected_options_summary

router = Router()

# --- Приватні функції для відображення UI ---

async def _show_category_menu(callback: CallbackQuery, product_repo: ProductRepository, state: FSMContext) -> None:
    # ... (не змінюється) ...
    """Показує користувачеві меню з категоріями товарів."""
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)
    
    categories_db = await product_repo.get_all_categories()
    categories_dto = [CategoryDTO.model_validate(c) for c in categories_db]
    
    await state.set_state(OrderState.in_menu)
    
    await callback.message.edit_text(
        "📝 **Меню PerkUP**. \n\nОберіть категорію, щоб переглянути доступні товари:",
        reply_markup=get_category_menu_keyboard(categories_dto, cart.calculate_total()),
        parse_mode="Markdown"
    )
    await callback.answer()
    
async def _show_products_list(callback: CallbackQuery, product_repo: ProductRepository, state: FSMContext, category_id: int) -> None:
    # ... (не змінюється) ...
    """Показує користувачеві список продуктів у вибраній категорії."""
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)
    
    products_db = await product_repo.get_products_by_category(category_id)
    products_dto = [ProductDTO.model_validate(p) for p in products_db]
    
    await state.update_data(current_category_id=category_id)
    await state.set_state(OrderState.in_category)
    
    await callback.message.edit_text(
        "☕️ **Вибір Напою/Товару**. \n\nОберіть позицію для додавання до кошика:",
        reply_markup=get_products_list_keyboard(products_dto, category_id, cart.calculate_total()),
        parse_mode="Markdown"
    )
    await callback.answer()

async def _show_configurator(callback: CallbackQuery, state: FSMContext) -> None:
    # ... (не змінюється) ...
    """Показує користувачеві інтерфейс конфігурації товару."""
    data = await state.get_data()
    
    # 1. Отримання даних про товар та вибрані опції з FSM
    config_data = data.get('current_product_config', {})
    product = ConfigurableProductDTO.model_validate(config_data)
    
    selected_ids: List[int] = data.get('selected_options_ids', [])
    quantity: int = data.get('current_quantity', 1)
    
    # 2. Формування текстового опису вибраних опцій
    current_price, selected_options = calculate_item_price(product, selected_ids)
    summary_text = get_selected_options_summary(selected_options)

    # 3. Формування повного повідомлення та клавіатури
    message_text = format_config_summary(product, selected_ids, summary_text)
    
    reply_markup = get_product_config_keyboard(product, selected_ids, quantity)

    # 4. Редагування повідомлення
    await callback.message.edit_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    await callback.answer()
    

# --- Приватна функція для відображення кошика ---
async def _show_cart_content(callback: CallbackQuery, state: FSMContext) -> None:
    """Генерує та відображає поточний вміст кошика."""
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)
    
    await state.set_state(OrderState.reviewing_cart)

    if not cart.items:
        await callback.message.edit_text(
            "🛒 **Ваш кошик порожній!** \n\nПочніть додавати товари з меню:",
            reply_markup=get_cart_keyboard(),
            parse_mode="Markdown"
        )
        return

    # Формування списку позицій
    items_list = []
    for i, item in enumerate(cart.items, 1):
        options_summary = "\n   " + get_selected_options_summary(item.selected_options).replace('\n', '\n   ')
        
        items_list.append(
            f"{i}. **{item.product_name}** ({item.unit_price:.2f} грн/шт)\n"
            f"   Кількість: **{item.quantity}**\n"
            f"   Опції:{options_summary}"
        )

    cart_text = (
        "🛒 **Ваш Кошик**\n\n"
        f"{'—' * 20}\n"
        f"{'\n'.join(items_list)}\n\n"
        f"**💵 Загальна сума**: **{cart.calculate_total():.2f} грн**"
    )

    await callback.message.edit_text(
        cart_text,
        reply_markup=get_cart_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# --- ХЕНДЛЕРИ КОШИКА ТА CHECKOUT ---

# --- 1. Обробник: Перейти до Кошика (show_cart) ---
@router.callback_query(F.data == "show_cart", F.state.in_({OrderState.in_menu, OrderState.in_category, OrderState.configuring_item, OrderState.reviewing_cart}))
async def show_cart_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """Відображає поточний вміст кошика."""
    await _show_cart_content(callback, state)


# --- 2. Обробник: Назад до Меню (з Кошика) ---
# Обробляється існуючим `back_to_main_menu_handler` у `start.py`, але для чистоти,
# створюємо окремий хендлер для продовження покупок, який повертає до категорій.
@router.callback_query(F.data == "back_to_menu", OrderState.reviewing_cart)
async def continue_shopping_handler(
    callback: CallbackQuery,
    product_repo: ProductRepository,
    state: FSMContext
) -> None:
    """Повертає з кошика до меню категорій, щоб продовжити покупки."""
    await _show_category_menu(callback, product_repo, state)


# --- 3. Обробник: Початок Оформлення Замовлення (start_checkout) ---
@router.callback_query(F.data == "start_checkout", OrderState.reviewing_cart)
async def start_checkout_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """
    Перехід до першого етапу оформлення: Вибір часу отримання.
    """
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)

    if not cart.items:
        await callback.answer("Кошик порожній! Не можна оформити замовлення.")
        return

    # Зберігаємо тимчасовий статус Checkout
    await state.set_state(OrderState.finalizing_order)
    
    await callback.message.edit_text(
        "🕒 **Оформлення Замовлення**\n\n"
        "**Загальна сума**: **{:.2f} грн**\n\n"
        "**Крок 1/2**: Оберіть зручний час отримання:".format(cart.calculate_total()),
        reply_markup=get_pickup_time_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer("Перехід до оформлення.")


# --- 4. Обробник: Вибір Часу Отримання (time:...) ---
@router.callback_query(Text(startswith="time:"), OrderState.finalizing_order)
async def select_pickup_time_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """Обробляє вибір часу отримання, зберігає його і переходить до вибору оплати."""
    time_key = callback.data.split(":")[1]
    
    # 1. Розрахунок часу
    pickup_time = datetime.now().replace(second=0, microsecond=0)
    
    if time_key == "now":
        # "Зараз" - додаємо 5 хвилин на приготування
        pickup_time += timedelta(minutes=5)
    else:
        minutes = int(time_key)
        # На певний час - округлюємо до найближчої хвилини інтервалу
        pickup_time += timedelta(minutes=minutes)

    # 2. Зберігання часу в FSM
    await state.update_data(
        pickup_time=pickup_time.isoformat(), # Зберігаємо як рядок ISO для FSM
    )
    
    # 3. Перехід до вибору оплати
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)
    
    await callback.message.edit_text(
        "💳 **Оформлення Замовлення**\n\n"
        f"**Час отримання**: **{pickup_time.strftime('%H:%M')}**\n"
        f"**Загальна сума**: **{cart.calculate_total():.2f} грн**\n\n"
        "**Крок 2/2**: Оберіть спосіб оплати:",
        reply_markup=get_payment_method_keyboard(cart.calculate_total()),
        parse_mode="Markdown"
    )
    await callback.answer(f"Час отримання встановлено на {pickup_time.strftime('%H:%M')}")


# --- 5. Обробник: Вибір Способу Оплати та Фіналізація Замовлення ---
@router.callback_query(Text(startswith="pay:"), OrderState.finalizing_order)
async def select_payment_and_finalize_handler(
    callback: CallbackQuery,
    user_repo: UserRepository,
    order_repo: OrderRepository,
    state: FSMContext
) -> None:
    """Обробляє вибір способу оплати, зберігає замовлення в БД та очищує FSM."""
    payment_method = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    # 1. Отримання всіх даних з FSM
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)
    pickup_time_iso = data.get('pickup_time')
    
    if not pickup_time_iso:
        await callback.answer("Помилка: Не вибрано час отримання. Почніть знову.")
        return

    pickup_time_dt = datetime.fromisoformat(pickup_time_iso)
    
    # 2. Збереження замовлення у БД (DDD: OrderRepository)
    try:
        new_order = await order_repo.create_full_order(
            cart=cart, 
            user_id=user_id, 
            pickup_time=pickup_time_dt,
            payment_method=payment_method.upper(),
        )
        await order_repo.session.commit()
        
        logger.success(f"New Order #{new_order.id} created by user {user_id}.")

        # 3. Очищення FSM
        await state.clear() 
        
        # 4. Фінальне повідомлення (UI/UX)
        final_message = (
            "🎉 **Ваше замовлення прийнято!**\n\n"
            f"**Номер замовлення**: **#{new_order.id}**\n"
            f"**Локація**: {(await order_repo.session.get(order_repo.location_model, new_order.location_id)).name}\n"
            f"**Час отримання**: {new_order.pickup_time.strftime('%H:%M')}\n"
            f"**До сплати**: {new_order.total_amount:.2f} грн\n"
            f"**Спосіб**: {payment_method.upper()}\n\n"
            "Ми повідомимо вас, коли замовлення буде готове. Дякуємо!"
        )
        
        await callback.message.edit_text(final_message, parse_mode="Markdown")
        await callback.answer(f"Замовлення #{new_order.id} успішно створено!")
        
    except Exception as e:
        logger.error(f"Error finalizing order for user {user_id}: {e}")
        await callback.answer("❌ Сталася помилка при оформленні замовлення. Спробуйте пізніше.")
        
# --- 6. Обробник: Назад до Часу Отримання (з Оплати) ---
@router.callback_query(F.data == "back_to_time_select", OrderState.finalizing_order)
async def back_to_time_select_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """Повертає до вибору часу отримання."""
    data = await state.get_data()
    # Очищуємо вибраний час, щоб користувач обрав його знову
    await state.update_data(pickup_time=None) 
    
    await callback.message.edit_text(
        "🕒 **Оформлення Замовлення**\n\n"
        f"**Загальна сума**: **{ShoppingCartDTO.model_validate(data).calculate_total():.2f} грн**\n\n"
        "**Крок 1/2**: Оберіть зручний час отримання:",
        reply_markup=get_pickup_time_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer("Повернення до вибору часу.")
