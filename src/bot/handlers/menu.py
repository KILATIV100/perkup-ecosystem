# src/bot/handlers/menu.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger
from typing import List
from datetime import datetime, timedelta
import re # Для обробки тексту оплати бонусами

# --- Репозиторії та Сервіси ---
from src.app.repositories.user_repo import UserRepository
from src.app.repositories.location_repo import LocationRepository
from src.app.repositories.product_repo import ProductRepository
from src.app.repositories.order_repo import OrderRepository
from src.app.services.loyalty_service import PosterLoyaltyService # <--- ІМПОРТ

# --- Клавіатури ---
from src.bot.keyboards.menu_kb import get_category_menu_keyboard
from src.bot.keyboards.main_menu import get_main_menu_keyboard
from src.bot.keyboards.product_kb import get_products_list_keyboard
from src.bot.keyboards.product_config_kb import get_product_config_keyboard, format_config_summary 
from src.bot.keyboards.cart_kb import get_cart_keyboard
from src.bot.keyboards.checkout_kb import get_pickup_time_keyboard, get_payment_method_keyboard 

# --- Domain/States/Utils ---
from src.app.domain.models import CategoryDTO, ProductDTO, ShoppingCartDTO, ConfigurableProductDTO, CartItemDTO, OptionDTO
from src.bot.states.order import OrderState
from src.app.utils.cart_utils import calculate_item_price, get_selected_options_summary
from src.db.models import User # Для Pydantic validation

router = Router()

# --- Приватні функції для відображення UI (зберігаються без змін) ---

async def _show_category_menu(callback: CallbackQuery, product_repo: ProductRepository, state: FSMContext) -> None:
    # ... (не змінюється) ...
    pass
    
async def _show_products_list(callback: CallbackQuery, product_repo: ProductRepository, state: FSMContext, category_id: int) -> None:
    # ... (не змінюється) ...
    pass

async def _show_configurator(callback: CallbackQuery, state: FSMContext) -> None:
    # ... (не змінюється) ...
    pass
    
async def _show_cart_content(callback: CallbackQuery, state: FSMContext) -> None:
    # ... (не змінюється) ...
    pass
    
# --- Приватна функція для відображення меню оплати (НОВА) ---
async def _show_payment_menu(callback: CallbackQuery, state: FSMContext, user: User, loyalty_service: PosterLoyaltyService) -> None:
    """Показує меню вибору оплати з урахуванням бонусів Poster POS."""
    data = await state.get_data()
    cart = ShoppingCartDTO.model_validate(data)
    total_amount = cart.calculate_total()
    
    available_points = 0
    
    # 1. Перевірка бонусів (тільки якщо є номер телефону)
    if user.phone_number:
        poster_info = await loyalty_service.get_client_info(user.phone_number)
        if poster_info and poster_info.get("is_registered"):
            available_points = poster_info.get('bonus_balance', 0)
            
    # 2. Отримання часу (для відображення)
    pickup_time_iso = data.get('pickup_time')
    pickup_time_dt = datetime.fromisoformat(pickup_time_iso) if pickup_time_iso else None

    # 3. Текст повідомлення
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


# --- ХЕНДЛЕРИ ---

# ... (start_order_handler, back_to_main_menu_handler, select_category_handler, back_to_categories_handler, select_product_handler, back_from_config_handler, toggle_option_handler, change_quantity_handler, add_to_cart_handler - БЕЗ ЗМІН) ...

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
        f"**Загальна сума**: **{cart.calculate_total():.2f} грн**\n\n"
        "**Крок 1/2**: Оберіть зручний час отримання:",
        reply_markup=get_pickup_time_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer("Перехід до оформлення.")


# --- 4. Обробник: Вибір Часу Отримання (time:...) ---
@router.callback_query(Text(startswith="time:"), OrderState.finalizing_order)
async def select_pickup_time_handler(
    callback: CallbackQuery,
    state: FSMContext,
    user_repo: UserRepository, # <--- ДОДАНО user_repo
    loyalty_service: PosterLoyaltyService # <--- ДОДАНО loyalty_service
) -> None:
    """Обробляє вибір часу отримання, зберігає його і переходить до вибору оплати."""
    time_key = callback.data.split(":")[1]
    
    # 1. Розрахунок часу
    pickup_time = datetime.now().replace(second=0, microsecond=0)
    
    if time_key == "now":
        pickup_time += timedelta(minutes=5)
    else:
        minutes = int(time_key)
        pickup_time += timedelta(minutes=minutes)

    # 2. Зберігання часу в FSM
    await state.update_data(
        pickup_time=pickup_time.isoformat(), 
    )
    
    # 3. Перехід до вибору оплати
    user_db = await user_repo.get_by_id(callback.from_user.id)
    await _show_payment_menu(callback, state, user_db, loyalty_service)


# --- 5. Обробник: Вибір Способу Оплати та Фіналізація Замовлення ---
@router.callback_query(Text(startswith="pay:"), OrderState.finalizing_order)
async def select_payment_and_finalize_handler(
    callback: CallbackQuery,
    user_repo: UserRepository,
    order_repo: OrderRepository,
    loyalty_service: PosterLoyaltyService, # <--- ДОДАНО СЕРВІС
    state: FSMContext
) -> None:
    """Обробляє вибір способу оплати, зберігає замовлення в БД та очищує FSM."""
    
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
    
    # --- ЛОГІКА СПИСАННЯ БОНУСІВ ---
    if payment_method == "bonus":
        if not user_db.phone_number:
            await callback.answer("❌ Для оплати бонусами потрібно прив'язати номер телефону у Профілі.")
            await state.set_state(OrderState.reviewing_cart)
            await _show_cart_content(callback, state) # Повертаємо до кошика
            return
            
        points_to_spend = int(payment_data[2]) # Отримуємо кількість балів
        
        # 1. Списання бонусів через Poster API
        if await loyalty_service.spend_points(user_db.phone_number, points_to_spend):
            points_used = points_to_spend
            total_paid = max(0.00, cart.total_amount - points_used) # Фінальна сума оплати
            payment_method = "BONUS_FULL" if total_paid == 0 else "BONUS_PARTIAL"
        else:
            await callback.answer("❌ Помилка списання бонусів. Можливо, недостатньо балів.")
            # Повернення до вибору оплати
            await _show_payment_menu(callback, state, user_db, loyalty_service)
            return

    # 2. Збереження замовлення у БД (DDD: OrderRepository)
    try:
        new_order = await order_repo.create_full_order(
            cart=cart, 
            user_id=user_id, 
            pickup_time=pickup_time_dt,
            payment_method=payment_method.upper(),
            points_used=points_used,
            # Нарахування бонусів (у Poster це відбувається автоматично, 
            # але ми фіксуємо потенційну суму для аудиту)
            points_earned=int(cart.total_amount * 0.05), # 5% кешбеку
        )
        await order_repo.session.commit()
        
        # 3. Якщо була онлайн-оплата, тут має бути перехід до платіжної системи

        # 4. Якщо оплата не була бонусами, нараховуємо бонуси через Poster (імітація)
        if payment_method not in ["BONUS_FULL", "BONUS_PARTIAL"]:
             await loyalty_service.accrue_points(user_db.phone_number or "guest", cart.total_amount)

        # 5. Очищення FSM
        await state.clear() 
        
        # 6. Фінальне повідомлення (UI/UX)
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


# --- 6. Обробник: Назад до Часу Отримання (з Оплати) ---
@router.callback_query(F.data == "back_to_time_select", OrderState.finalizing_order)
async def back_to_time_select_handler(
    callback: CallbackQuery,
    state: FSMContext
) -> None:
    """Повертає до вибору часу отримання."""
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
