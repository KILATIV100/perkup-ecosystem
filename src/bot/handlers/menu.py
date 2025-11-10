# src/bot/handlers/menu.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger
from src.app.repositories.user_repo import UserRepository
from src.app.repositories.location_repo import LocationRepository
from src.app.repositories.product_repo import ProductRepository
from src.bot.keyboards.menu_kb import get_category_menu_keyboard
from src.bot.keyboards.main_menu import get_main_menu_keyboard
from src.bot.keyboards.product_kb import get_products_list_keyboard # <--- НОВИЙ ІМПОРТ
from src.app.domain.models import CategoryDTO, ProductDTO, ShoppingCartDTO, ConfigurableProductDTO
from src.bot.states.order import OrderState

router = Router()

# --- Приватна функція для відображення меню категорій (для використання з різних точок) ---
async def _show_category_menu(callback: CallbackQuery, product_repo: ProductRepository, state: FSMContext) -> None:
    """Показує користувачеві меню з категоріями товарів."""
    
    # 1. Отримання даних з FSM
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)
    
    # 2. Отримання категорій з БД
    categories_db = await product_repo.get_all_categories()
    categories_dto = [CategoryDTO.model_validate(c) for c in categories_db]
    
    # 3. Перехід у стан 'in_menu'
    await state.set_state(OrderState.in_menu)
    
    # 4. Редагування повідомлення (UI/UX)
    await callback.message.edit_text(
        "📝 **Меню PerkUP**. \n\nОберіть категорію, щоб переглянути доступні товари:",
        reply_markup=get_category_menu_keyboard(categories_dto, cart.calculate_total()),
        parse_mode="Markdown"
    )
    await callback.answer()
    
# --- Приватна функція для відображення списку продуктів ---
async def _show_products_list(callback: CallbackQuery, product_repo: ProductRepository, state: FSMContext, category_id: int) -> None:
    """Показує користувачеві список продуктів у вибраній категорії."""
    
    # 1. Отримання даних з FSM
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)
    
    # 2. Отримання продуктів з БД
    products_db = await product_repo.get_products_by_category(category_id)
    products_dto = [ProductDTO.model_validate(p) for p in products_db]
    
    # 3. Зберігаємо поточну категорію у FSM
    await state.update_data(current_category_id=category_id)
    await state.set_state(OrderState.in_category)
    
    # 4. Редагування повідомлення
    await callback.message.edit_text(
        "☕️ **Вибір Напою/Товару**. \n\nОберіть позицію для додавання до кошика:",
        reply_markup=get_products_list_keyboard(products_dto, category_id, cart.total_amount),
        parse_mode="Markdown"
    )
    await callback.answer()


# --- 1. Обробник: Початок Замовлення (з Головного Меню) ---
@router.callback_query(F.data == "start_order")
async def start_order_handler(
    callback: CallbackQuery,
    user_repo: UserRepository,
    product_repo: ProductRepository,
    state: FSMContext
) -> None:
    """
    Початок процесу оформлення замовлення. Ініціалізує FSM для кошика та переходить до меню.
    """
    user_db = await user_repo.get_by_id(callback.from_user.id)
    
    # ПЕРЕВІРКА: Локація має бути обрана
    if user_db.preferred_location_id is None:
        await callback.answer("🚨 Спочатку оберіть локацію в меню /start!")
        return
    
    # Ініціалізація кошика у FSM 
    cart = ShoppingCartDTO(location_id=user_db.preferred_location_id, items=[])
    await state.set_data(cart.model_dump())
    
    logger.info(f"User {callback.from_user.id} started new order.")
    
    await _show_category_menu(callback, product_repo, state)


# --- 2. Обробник: Назад до Категорій (з Меню Продуктів) ---
@router.callback_query(F.data == "back_to_cat_list", OrderState.in_category)
async def back_to_categories_handler(
    callback: CallbackQuery,
    product_repo: ProductRepository,
    state: FSMContext
) -> None:
    """Повертає користувача зі списку продуктів назад до списку категорій."""
    await _show_category_menu(callback, product_repo, state)


# --- 3. Обробник: Вибір Категорії ---
@router.callback_query(Text(startswith="select_cat:"), OrderState.in_menu)
async def select_category_handler(
    callback: CallbackQuery,
    product_repo: ProductRepository,
    state: FSMContext
) -> None:
    """
    Обробляє вибір категорії та показує список продуктів у ній.
    """
    category_id = int(callback.data.split(":")[1])
    
    # Отримання продуктів та відображення списку
    await _show_products_list(callback, product_repo, state, category_id)


# --- 4. Обробник: Вибір Продукту -> Перехід до Конфігурації ---
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
    
    # 1. Отримання продукту з опціями (використовуючи жадібне завантаження)
    product_db = await product_repo.get_product_with_options(product_id)
    
    if not product_db:
        await callback.answer("Цей товар не знайдено або він недоступний.")
        return

    # 2. Формування DTO з доступними опціями
    options_list = [ConfigurableProductDTO.model_validate(link.option) 
                    for link in product_db.options_links]
    
    # 3. Створення ConfigurableProductDTO
    config_product = ConfigurableProductDTO.model_validate(product_db, context={'available_options': options_list})
    config_product.available_options = options_list # Оновлення списку опцій
    
    # 4. Перевірка: Чи є опції для конфігурації?
    if not config_product.available_options:
        # 4.1. Якщо опцій немає -> Одразу додаємо до кошика
        # ЦЮ ЛОГІКУ МИ РЕАЛІЗУЄМО НА НАСТУПНОМУ КРОЦІ
        await callback.answer(f"✅ Товар '{config_product.name}' додано до кошика (тимчасово).")
        
        # Повертаємо користувача до списку продуктів (або до кошика)
        data = await state.get_data()
        category_id = data.get('current_category_id')
        if category_id:
             await _show_products_list(callback, product_repo, state, category_id)
        
    else:
        # 4.2. Якщо опції є -> Переходимо у стан конфігурації
        await state.update_data(
            current_product_config=config_product.model_dump(),
            selected_options_ids=[] # Ініціалізація вибраних опцій
        )
        await state.set_state(OrderState.configuring_item)
        
        # ЦЮ ЛОГІКУ ВІДОБРАЖЕННЯ КОНФІГУРАТОРА МИ ТЕЖ РЕАЛІЗУЄМО НА НАСТУПНОМУ КРОЦІ
        await callback.answer(f"Перехід до конфігурації '{config_product.name}'.")
        
        # Тимчасове повідомлення
        await callback.message.edit_text(
            f"**Конфігурація**: {config_product.name}. Потрібно реалізувати UI опцій.",
            reply_markup=None
        )
