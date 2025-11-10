# src/bot/handlers/menu.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger
from typing import List

# --- Репозиторії ---
from src.app.repositories.user_repo import UserRepository
from src.app.repositories.location_repo import LocationRepository
from src.app.repositories.product_repo import ProductRepository

# --- Клавіатури ---
from src.bot.keyboards.menu_kb import get_category_menu_keyboard
from src.bot.keyboards.main_menu import get_main_menu_keyboard
from src.bot.keyboards.product_kb import get_products_list_keyboard
from src.bot.keyboards.product_config_kb import get_product_config_keyboard, format_config_summary 

# --- Domain/States/Utils ---
from src.app.domain.models import CategoryDTO, ProductDTO, ShoppingCartDTO, ConfigurableProductDTO, CartItemDTO, OptionDTO
from src.bot.states.order import OrderState
from src.app.utils.cart_utils import calculate_item_price, get_selected_options_summary

router = Router()

# --- Приватні функції для відображення UI ---

async def _show_category_menu(callback: CallbackQuery, product_repo: ProductRepository, state: FSMContext) -> None:
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


# --- 1. Обробник: Початок Замовлення ---
@router.callback_query(F.data == "start_order")
async def start_order_handler(
    callback: CallbackQuery,
    user_repo: UserRepository,
    product_repo: ProductRepository,
    state: FSMContext
) -> None:
    """Початок процесу оформлення замовлення."""
    user_db = await user_repo.get_by_id(callback.from_user.id)
    
    if user_db.preferred_location_id is None:
        await callback.answer("🚨 Спочатку оберіть локацію в меню /start!")
        return
    
    cart = ShoppingCartDTO(location_id=user_db.preferred_location_id, items=[])
    # Використовуємо .model_dump() для зберігання у FSM
    await state.set_data(cart.model_dump()) 
    
    logger.info(f"User {callback.from_user.id} started new order.")
    
    await _show_category_menu(callback, product_repo, state)


# --- 2. Обробник: Назад до Головного Меню ---
@router.callback_query(F.data == "back_to_main", F.state.in_({OrderState.in_menu, OrderState.in_category, OrderState.configuring_item, OrderState.reviewing_cart}))
async def back_to_main_menu_handler(
    callback: CallbackQuery,
    user_repo: UserRepository,
    location_repo: LocationRepository, 
    state: FSMContext
) -> None:
    """Повернення користувача з будь-якого етапу замовлення на головний екран."""
    await state.clear() 
    
    user_db = await user_repo.get_by_id(callback.from_user.id)
    
    if user_db and user_db.preferred_location_id:
        location = await location_repo.get_by_id(user_db.preferred_location_id)
        location_name = location.name if location else "Невідома локація"
        
        await callback.message.edit_text(
            f"🏡 **Головне Меню**. \n\nВаша поточна локація: **{location_name}**",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer("Повернення до головного меню.")
    else:
        await callback.message.edit_text("Будь ласка, почніть з команди /start, щоб вибрати локацію.")
        await callback.answer()


# --- 3. Обробник: Вибір Категорії ---
@router.callback_query(Text(startswith="select_cat:"), OrderState.in_menu)
async def select_category_handler(
    callback: CallbackQuery,
    product_repo: ProductRepository,
    state: FSMContext
) -> None:
    """Обробляє вибір категорії та показує список продуктів у ній."""
    category_id = int(callback.data.split(":")[1])
    await _show_products_list(callback, product_repo, state, category_id)


# --- 4. Обробник: Назад до Категорій ---
@router.callback_query(F.data == "back_to_cat_list", OrderState.in_category)
async def back_to_categories_handler(
    callback: CallbackQuery,
    product_repo: ProductRepository,
    state: FSMContext
) -> None:
    """Повертає користувача зі списку продуктів назад до списку категорій."""
    await _show_category_menu(callback, product_repo, state)


# --- 5. Обробник: Вибір Продукту -> Перехід до Конфігурації/Додавання ---
@router.callback_query(Text(startswith="select_prod:"), OrderState.in_category)
async def select_product_handler(
    callback: CallbackQuery,
    product_repo: ProductRepository,
    state: FSMContext
) -> None:
    """
    Обробляє вибір продукту. Перевіряє наявність опцій та переходить 
    або до конфігурації, або одразу додає до кошика.
    """
    product_id = int(callback.data.split(":")[1])
    product_db = await product_repo.get_product_with_options(product_id)
    
    if not product_db:
        await callback.answer("Цей товар не знайдено або він недоступний.")
        return

    # 1. Формування ConfigurableProductDTO
    options_list = [OptionDTO.model_validate(link.option) for link in product_db.options_links]
    config_product = ConfigurableProductDTO.model_validate(product_db, update={'available_options': options_list})
    
    # 2. Перевірка: Чи є опції для конфігурації?
    if not config_product.available_options:
        # 2.1. Якщо опцій немає -> Одразу додаємо до кошика
        cart_item = CartItemDTO(
            product_id=product_id,
            product_name=config_product.name,
            quantity=1,
            unit_price=config_product.base_price,
            selected_options=[]
        )
        
        data = await state.get_data()
        cart = ShoppingCartDTO.model_validate(data)
        
        cart.items.append(cart_item)
        cart.calculate_total()
        
        # Зберігаємо оновлений кошик
        await state.set_data(cart.model_dump())
        
        await callback.answer(f"✅ Товар '{config_product.name}' додано до кошика ({config_product.base_price:.2f} грн).")
        
        # Повертаємо користувача до списку продуктів
        category_id = data.get('current_category_id')
        if category_id:
             await _show_products_list(callback, product_repo, state, category_id)
        
    else:
        # 2.2. Якщо опції є -> Переходимо у стан конфігурації
        await state.update_data(
            current_product_config=config_product.model_dump(),
            selected_options_ids=[], # Ініціалізація вибраних опцій
            current_quantity=1
        )
        await state.set_state(OrderState.configuring_item)
        await _show_configurator(callback, state)


# --- 6. Обробник: Скасування Конфігурації -> Назад до Продуктів ---
@router.callback_query(F.data == "back_to_menu", OrderState.configuring_item)
async def back_from_config_handler(
    callback: CallbackQuery,
    product_repo: ProductRepository,
    state: FSMContext
) -> None:
    """Скасування конфігурації товару та повернення до списку продуктів."""
    data = await state.get_data()
    category_id = data.get('current_category_id')
    
    # Очищуємо тимчасові дані конфігурації
    await state.update_data(current_product_config=None, selected_options_ids=None, current_quantity=None)
    
    if category_id:
        # Повертаємось у стан меню, але поки що показуємо список продуктів
        await state.set_state(OrderState.in_category) 
        await _show_products_list(callback, product_repo, state, category_id)
        await callback.answer("Конфігурацію скасовано.")
    else:
        await _show_category_menu(callback, product_repo, state) # Fallback


# --- 7. Обробник: Зміна Опції (Toggle Option) ---
@router.callback_query(Text(startswith="toggle_opt:"), OrderState.configuring_item)
async def toggle_option_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """Вмикає або вимикає опцію товару. Обробляє групи опцій (вибір одного з групи)."""
    option_id = int(callback.data.split(":")[1])
    
    data = await state.get_data()
    selected_ids: List[int] = data.get('selected_options_ids', [])
    config_data = data.get('current_product_config', {})
    product = ConfigurableProductDTO.model_validate(config_data)

    new_selected_ids = list(selected_ids)
    
    toggled_option = next((opt for opt in product.available_options if opt.id == option_id), None)

    if not toggled_option:
        await callback.answer("Помилка: опцію не знайдено.")
        return

    if option_id in new_selected_ids:
        # ВИМКНЕННЯ: Просто видаляємо опцію зі списку
        new_selected_ids.remove(option_id)
        
    else:
        # УВІМКНЕННЯ: Перевіряємо групу опцій
        
        # Визначаємо, чи є вже вибрана опція з цієї ж групи
        group_id_to_remove = None
        for selected_opt_id in new_selected_ids:
            # Знаходимо DTO вибраної опції
            selected_option = next((opt for opt in product.available_options if opt.id == selected_opt_id), None)
            
            if selected_option and selected_option.option_group == toggled_option.option_group:
                # Знайшли опцію з тієї ж групи -> її потрібно видалити
                group_id_to_remove = selected_opt_id
                break
        
        # Видаляємо стару опцію з цієї ж групи
        if group_id_to_remove is not None:
            new_selected_ids.remove(group_id_to_remove)
            
        # Додаємо нову опцію
        new_selected_ids.append(option_id)
        
        # Сортуємо для консистентності
        new_selected_ids.sort()

    # Зберігаємо новий стан
    await state.update_data(selected_options_ids=new_selected_ids)
    
    # Перемальовуємо інтерфейс
    await _show_configurator(callback, state)


# --- 8. Обробник: Зміна Кількості ---
@router.callback_query(Text(startswith="change_qty:"), OrderState.configuring_item)
async def change_quantity_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """Змінює кількість товару в конфігураторі."""
    change = int(callback.data.split(":")[1])
    
    data = await state.get_data()
    current_quantity = data.get('current_quantity', 1)
    
    new_quantity = current_quantity + change
    
    if new_quantity < 1:
        await callback.answer("Кількість не може бути меншою за 1.")
        return
        
    await state.update_data(current_quantity=new_quantity)
    
    # Перемальовуємо інтерфейс
    await _show_configurator(callback, state)


# --- 9. Обробник: Додати до Кошика (Фіналізація) ---
@router.callback_query(F.data == "add_to_cart", OrderState.configuring_item)
async def add_to_cart_handler(
    callback: CallbackQuery,
    product_repo: ProductRepository,
    state: FSMContext
) -> None:
    """Обчислює фінальну ціну товару з опціями та додає його до кошика."""
    data = await state.get_data()
    
    # 1. Отримання всіх даних для CartItemDTO
    config_data = data.get('current_product_config', {})
    product = ConfigurableProductDTO.model_validate(config_data)
    selected_ids: List[int] = data.get('selected_options_ids', [])
    quantity: int = data.get('current_quantity', 1)

    # 2. Обчислення фінальної ціни та отримання DTO опцій
    final_price, selected_options = calculate_item_price(product, selected_ids)
    
    # 3. Створення об'єкта CartItemDTO
    cart_item = CartItemDTO(
        product_id=product.id,
        product_name=product.name,
        quantity=quantity,
        unit_price=final_price, # Ціна одиниці з опціями
        selected_options=selected_options
    )
    
    # 4. Оновлення ShoppingCartDTO
    cart = ShoppingCartDTO.model_validate(data)
    cart.items.append(cart_item)
    cart.calculate_total()
    
    # 5. Зберігаємо оновлений кошик та очищуємо тимчасові дані конфігурації
    await state.set_data(cart.model_dump())
    await state.update_data(current_product_config=None, selected_options_ids=None, current_quantity=None)
    
    # Повертаємось у стан меню, але поки що показуємо список продуктів
    await state.set_state(OrderState.in_category) 
    
    # 6. UI/UX: Повідомлення про додавання та оновлення меню
    await callback.answer(f"✅ Додано: {quantity} x {product.name} ({final_price * quantity:.2f} грн).")
    
    # Повертаємо користувача до списку продуктів
    category_id = data.get('current_category_id')
    if category_id:
        await _show_products_list(callback, product_repo, state, category_id)
    else:
        await _show_category_menu(callback, product_repo, state) # Fallback
