# src/bot/handlers/menu.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger
from src.app.repositories.user_repo import UserRepository
from src.app.repositories.location_repo import LocationRepository
from src.app.repositories.product_repo import ProductRepository
from src.db.models import User 
from src.bot.keyboards.menu_kb import get_category_menu_keyboard
from src.bot.keyboards.main_menu import get_main_menu_keyboard
from src.app.domain.models import CategoryDTO, ShoppingCartDTO
from src.bot.states.order import OrderState

router = Router()

# --- Приватна функція для відображення меню категорій ---
async def _show_category_menu(callback: CallbackQuery, product_repo: ProductRepository, state: FSMContext) -> None:
    """Показує користувачеві меню з категоріями товарів."""
    
    # 1. Отримання даних з FSM
    data = await state.get_data()
    
    # Ініціалізуємо кошик (якщо його ще немає)
    cart = ShoppingCartDTO.model_validate(data)
    
    # 2. Отримання категорій з БД
    categories_db = await product_repo.get_all_categories()
    categories_dto = [CategoryDTO.model_validate(c) for c in categories_db]
    
    # 3. Перехід у стан 'in_menu'
    await state.set_state(OrderState.in_menu)
    
    # 4. Редагування повідомлення (UI/UX)
    await callback.message.edit_text(
        "📝 **Меню PerkUP**. \n\nОберіть категорію, щоб переглянути доступні товари:",
        reply_markup=get_category_menu_keyboard(categories_dto, cart.total_amount),
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
    Початок процесу оформлення замовлення.
    Перевіряє, чи вибрана локація. Ініціалізує FSM для кошика.
    """
    user_id = callback.from_user.id
    user_db = await user_repo.get_by_id(user_id)
    
    if user_db.preferred_location_id is None:
        await callback.answer("🚨 Спочатку оберіть локацію в меню /start!")
        return
    
    # 1. Ініціалізація кошика у FSM (зберігаємо локацію)
    cart = ShoppingCartDTO(location_id=user_db.preferred_location_id, items=[])
    await state.set_data(cart.model_dump())
    
    logger.info(f"User {user_id} started new order at location {user_db.preferred_location_id}.")
    
    await _show_category_menu(callback, product_repo, state)


# --- 2. Обробник: Назад до Головного Меню (з Меню Категорій) ---
@router.callback_query(F.data == "back_to_main", F.state.in_({OrderState.in_menu, OrderState.in_category, OrderState.configuring_item, OrderState.reviewing_cart}))
async def back_to_main_menu_handler(
    callback: CallbackQuery,
    user_repo: UserRepository,
    location_repo: LocationRepository, 
    state: FSMContext
) -> None:
    """
    Повернення користувача з будь-якого етапу замовлення на головний екран.
    """
    # Очищуємо FSM контекст, оскільки замовлення скасовано
    await state.clear() 
    
    user_db = await user_repo.get_by_id(callback.from_user.id)
    
    if user_db and user_db.preferred_location_id:
        # Використовуємо .get() замість .get_by_id() для LocationRepository
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
    """
    Обробляє вибір категорії та показує список продуктів у ній.
    """
    category_id = int(callback.data.split(":")[1])
    
    # 1. Отримати продукти за category_id
    products_db = await product_repo.get_products_by_category(category_id)
    
    if not products_db:
        await callback.answer("У цій категорії поки що немає товарів.")
        return

    # 2. Тут має бути логіка створення клавіатури зі списком продуктів.
    # Тимчасовий відповідь:
    product_names = [p.name for p in products_db]
    await callback.message.edit_text(
        f"**Товари в категорії ID={category_id}**:\n\n" + "\n".join(product_names),
        reply_markup=callback.message.reply_markup, # Поки що залишаємо попереднє меню
        parse_mode="Markdown"
    )
    
    # 3. Змінюємо стан на OrderState.in_category
    await state.set_state(OrderState.in_category)
    await callback.answer()
