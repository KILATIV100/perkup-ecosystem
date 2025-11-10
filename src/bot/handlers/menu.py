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
from src.app.repositories.order_repo import OrderRepository

# --- Сервіси та Утиліти ---
from src.app.services.loyalty_service import PosterLoyaltyService
from src.app.utils.cart_utils import calculate_item_price, get_selected_options_summary

# --- Клавіатури ---
from src.bot.keyboards.menu_kb import get_category_menu_keyboard
from src.bot.keyboards.main_menu import get_main_menu_keyboard
from src.bot.keyboards.product_kb import get_products_list_keyboard
from src.bot.keyboards.product_config_kb import get_product_config_keyboard, format_config_summary 
from src.bot.keyboards.cart_kb import get_cart_keyboard
from src.bot.keyboards.checkout_kb import get_pickup_time_keyboard, get_payment_method_keyboard 

# --- Domain/States ---
from src.app.domain.models import CategoryDTO, ProductDTO, ShoppingCartDTO, ConfigurableProductDTO, CartItemDTO, OptionDTO
from src.bot.states.order import OrderState
from src.db.models import User 

# --- Імпорти з інших хендлерів ---
from src.bot.handlers.start import _show_main_menu # Для повернення до головного меню

router = Router()

# --- Приватні функції для відображення UI ---
# (не змінюються, але тут потрібен імпорт _show_main_menu)

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
    
    config_data = data.get('current_product_config', {})
    product = ConfigurableProductDTO.model_validate(config_data)
    
    selected_ids: List[int] = data.get('selected_options_ids', [])
    quantity: int = data.get('current_quantity', 1)
    
    current_price, selected_options = calculate_item_price(product, selected_ids)
    summary_text = get_selected_options_summary(selected_options)

    message_text = format_config_summary(product, selected_ids, summary_text)
    
    reply_markup = get_product_config_keyboard(product, selected_ids, quantity)

    await callback.message.edit_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    await callback.answer()
    
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

async def _show_payment_menu(callback: CallbackQuery, state: FSMContext, user: User, loyalty_service: PosterLoyaltyService) -> None:
    """Показує меню вибору оплати з урахуванням бонусів Poster POS."""
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)
    total_amount = cart.calculate_total()
    
    available_points = 0
    
    if user.phone_number:
        poster_info = await loyalty_service.get_client_info(user.phone_number)
        
        if poster_info and poster_info.get("is_registered"):
            available_points = poster_info.get('bonus_balance', 0)
            
    pickup_time_iso = data.get('pickup_time')
    pickup_time_dt = datetime.fromisoformat(pickup_time_iso) if pickup_time_iso else None

    text = (
        "💳 **Оформлення Замовлення**\n\n"
        f"**Час отримання**: **{pickup_time_dt.strftime('%H:%M')}**\n"
        f"**Загальна сума**: **{total_amount:.2f} грн**\n\n"
        "**Крок 2/2**: Оберіть спосіб оплати:"
    )
    if available_points > 0:
         text += f"\n✨ *Доступно бонусів*: **{available_points}**"
    elif not user.phone_number:
         text += "\n⚠️ *Бонуси недоступні*: Не прив'язано номер телефону."

    await callback.message.edit_text(
        text,
        reply_markup=get_payment_method_keyboard(total_amount, available_points),
        parse_mode="Markdown"
    )
    await callback.answer()


# --- ХЕНДЛЕРИ КОШИКА ТА CHECKOUT ---

# --- 1. Обробник: Початок Замовлення (з Головного Меню) ---
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
    await state.set_data(cart.model_dump()) 
    
    logger.info(f"User {callback.from_user.id} started new order.")
    
    await _show_category_menu(callback, product_repo, state)


# --- 2. Обробник: Назад до Головного Меню (з Меню Категорій) ---
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
        await _show_main_menu(callback, user_db, location_name)
        await callback.answer("Повернення до головного меню.")
    else:
        await callback.message.edit_text("Будь ласка, почніть з команди /start, щоб вибрати локацію.")
        await callback.answer()


# --- 3. Обробник: Вибір Категорії ---
@router.callback_query(F.data.startswith("select_cat:"), OrderState.in_menu) # <--- ВИПРАВЛЕНО
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
@router.callback_query(F.data.startswith("select_prod:"), OrderState.in_category) # <--- ВИПРАВЛЕНО
async def select_product_handler(
    callback: CallbackQuery,
    product_repo: ProductRepository,
    state: FSMContext
) -> None:
    """Обробляє вибір продукту. Перевіряє наявність опцій та переходить 
    або до конфігурації, або одразу додає до кошика."""
    product_id = int(callback.data.split(":")[1])
    product_db = await product_repo.get_product_with_options(product_id)
    
    if not product_db:
        await callback.answer("Цей товар не знайдено або він недоступний.")
        return

    options_list = [OptionDTO.model_validate(link.option) for link in product_db.options_links]
    config_product = ConfigurableProductDTO.model_validate(product_db, update={'available_options': options_list})
    
    if not config_product.available_options:
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
        
        await state.set_data(cart.model_dump())
        
        await callback.answer(f"✅ Товар '{config_product.name}' додано до кошика ({config_product.base_price:.2f} грн).")
        
        category_id = data.get('current_category_id')
        if category_id:
             await _show_products_list(callback, product_repo, state, category_id)
        
    else:
        await state.update_data(
            current_product_config=config_product.model_dump(),
            selected_options_ids=[], 
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
    
    await state.update_data(current_product_config=None, selected_options_ids=None, current_quantity=None)
    
    if category_id:
        await state.set_state(OrderState.in_category) 
        await _show_products_list(callback, product_repo, state, category_id)
        await callback.answer("Конфігурацію скасовано.")
    else:
        await _show_category_menu(callback, product_repo, state) 


# --- 7. Обробник: Зміна Опції (Toggle Option) ---
@router.callback_query(F.data.startswith("toggle_opt:"), OrderState.configuring_item) # <--- ВИПРАВЛЕНО
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
        new_selected_ids.remove(option_id)
        
    else:
        group_id_to_remove = None
        for selected_opt_id in new_selected_ids:
            selected_option = next((opt for opt in product.available_options if opt.id == selected_opt_id), None)
            
            if selected_option and selected_option.option_group == toggled_option.option_group:
                group_id_to_remove = selected_opt_id
                break
        
        if group_id_to_remove is not None:
            new_selected_ids.remove(group_id_to_remove)
            
        new_selected_ids.append(option_id)
        new_selected_ids.sort()

    await state.update_data(selected_options_ids=new_selected_ids)
    
    await _show_configurator(callback, state)


# --- 8. Обробник: Зміна Кількості ---
@router.callback_query(F.data.startswith("change_qty:"), OrderState.configuring_item) # <--- ВИПРАВЛЕНО
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
    
    config_data = data.get('current_product_config', {})
    product = ConfigurableProductDTO.model_validate(config_data)
    selected_ids: List[int] = data.get('selected_options_ids', [])
    quantity: int = data.get('current_quantity', 1)

    final_price, selected_options = calculate_item_price(product, selected_ids)
    
    cart_item = CartItemDTO(
        product_id=product.id,
        product_name=product.name,
        quantity=quantity,
        unit_price=final_price, 
        selected_options=selected_options
    )
    
    cart = ShoppingCartDTO.model_validate(data)
    cart.items.append(cart_item)
    cart.calculate_total()
    
    await state.set_data(cart.model_dump())
    await state.update_data(current_product_config=None, selected_options_ids=None, current_quantity=None)
    
    await state.set_state(OrderState.in_category) 
    
    await callback.answer(f"✅ Додано: {quantity} x {product.name} ({final_price * quantity:.2f} грн).")
    
    category_id = data.get('current_category_id')
    if category_id:
        await _show_products_list(callback, product_repo, state, category_id)
    else:
        await _show_category_menu(callback, product_repo, state)


# --- ХЕНДЛЕРИ КОШИКА ТА CHECKOUT (без змін) ---
# ... (всі інші хендлери залишаються без змін) ...
@router.callback_query(F.data == "show_cart", F.state.in_({OrderState.in_menu, OrderState.in_category, OrderState.configuring_item, OrderState.reviewing_cart}))
async def show_cart_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await _show_cart_content(callback, state)

@router.callback_query(F.data == "back_to_menu", OrderState.reviewing_cart)
async def continue_shopping_handler(callback: CallbackQuery, product_repo: ProductRepository, state: FSMContext) -> None:
    await _show_category_menu(callback, product_repo, state)

@router.callback_query(F.data == "start_checkout", OrderState.reviewing_cart)
async def start_checkout_handler(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)
    if not cart.items:
        await callback.answer("Кошик порожній! Не можна оформити замовлення.")
        return
    await state.set_state(OrderState.finalizing_order)
    await callback.message.edit_text(
        "🕒 **Оформлення Замовлення**\n\n"
        f"**Загальна сума**: **{cart.calculate_total():.2f} грн**\n\n"
        "**Крок 1/2**: Оберіть зручний час отримання:",
        reply_markup=get_pickup_time_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer("Перехід до оформлення.")

@router.callback_query(F.data.startswith("time:"), OrderState.finalizing_order)
async def select_pickup_time_handler(
    callback: CallbackQuery,
    state: FSMContext,
    user_repo: UserRepository,
    loyalty_service: PosterLoyaltyService
) -> None:
    time_key = callback.data.split(":")[1]
    pickup_time = datetime.now().replace(second=0, microsecond=0)
    if time_key == "now":
        pickup_time += timedelta(minutes=5)
    else:
        minutes = int(time_key)
        pickup_time += timedelta(minutes=minutes)
    await state.update_data(pickup_time=pickup_time.isoformat())
    user_db = await user_repo.get_by_id(callback.from_user.id)
    await _show_payment_menu(callback, state, user_db, loyalty_service)

@router.callback_query(F.data.startswith("pay:"), OrderState.finalizing_order)
async def select_payment_and_finalize_handler(
    callback: CallbackQuery,
    user_repo: UserRepository,
    order_repo: OrderRepository,
    loyalty_service: PosterLoyaltyService,
    state: FSMContext
) -> None:
    payment_data = callback.data.split(":")
    payment_method = payment_data[1]
    user_id = callback.from_user.id
    user_db = await user_repo.get_by_id(user_id)
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)
    pickup_time_iso = data.get('pickup_time')
    if not pickup_time_iso:
        await callback.answer("Помилка: Не вибрано час отримання. Почніть знову.")
        return
    pickup_time_dt = datetime.fromisoformat(pickup_time_iso)
    points_used = 0
    total_paid = cart.total_amount
    
    if payment_method == "bonus":
        if not user_db.phone_number:
            await callback.answer("❌ Для оплати бонусами потрібно прив'язати номер телефону у Профілі.")
            await state.set_state(OrderState.reviewing_cart)
            await _show_cart_content(callback, state)
            return
        points_to_spend = int(payment_data[2])
        if await loyalty_service.spend_points(user_db.phone_number, points_to_spend):
            points_used = points_to_spend
            total_paid = max(0.00, cart.total_amount - points_used)
            payment_method = "BONUS_FULL" if total_paid == 0 else "BONUS_PARTIAL"
        else:
            await callback.answer("❌ Помилка списання бонусів. Можливо, недостатньо балів.")
            await _show_payment_menu(callback, state, user_db, loyalty_service)
            return

    try:
        new_order = await order_repo.create_full_order(
            cart=cart, 
            user_id=user_id, 
            pickup_time=pickup_time_dt,
            payment_method=payment_method.upper(),
            points_used=points_used,
            points_earned=int(cart.total_amount * 0.05),
        )
        await order_repo.session.commit()
        
        if payment_method not in ["BONUS_FULL", "BONUS_PARTIAL"]:
             await loyalty_service.accrue_points(user_db.phone_number or "guest", cart.total_amount)

        await state.clear() 
        
        final_message = (
            "🎉 **Ваше замовлення прийнято!**\n\n"
            f"**Номер замовлення**: **#{new_order.id}**\n"
            f"**Локація**: {(await order_repo.session.get(order_repo.location_model, new_order.location_id)).name}\n"
            f"**Час отримання**: {new_order.pickup_time.strftime('%H:%M')}\n"
            f"**Сплачено бонусами**: **{points_used}** грн\n"
            f"**До сплати (фінально)**: **{total_paid:.2f} грн**\n"
            f"**Спосіб оплати**: {new_order.payment_method}\n\n"
            "Ми повідомимо вас, коли замовлення буде готове. Дякуємо!"
        )
        
        await callback.message.edit_text(final_message, parse_mode="Markdown")
        await callback.answer(f"Замовлення #{new_order.id} успішно створено!")
        
    except Exception as e:
        logger.error(f"Error finalizing order for user {user_id}: {e}")
        await callback.answer("❌ Сталася помилка при оформленні замовлення. Спробуйте пізніше.")


@router.callback_query(F.data == "back_to_time_select", OrderState.finalizing_order)
async def back_to_time_select_handler(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(pickup_time=None) 
    await callback.message.edit_text(
        "🕒 **Оформлення Замовлення**\n\n"
        f"**Загальна сума**: **{ShoppingCartDTO.model_validate(data).calculate_total():.2f} грн**\n\n"
        "**Крок 1/2**: Оберіть зручний час отримання:",
        reply_markup=get_pickup_time_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer("Повернення до вибору часу.")
