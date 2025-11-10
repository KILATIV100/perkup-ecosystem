# src/bot/handlers/profile.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from loguru import logger
import re

# --- Репозиторії та Сервіси ---
from src.app.repositories.user_repo import UserRepository
from src.app.repositories.location_repo import LocationRepository
from src.app.services.loyalty_service import PosterLoyaltyService
from src.db.models import User
from src.bot.states.order import ProfileState, OrderState # <--- ДОДАНО OrderState для зміни локації
from src.bot.keyboards.profile_kb import get_profile_main_keyboard, get_request_contact_reply_keyboard, get_remove_reply_keyboard
from src.bot.handlers.start import _show_main_menu, _show_location_selection # <--- Імпорт приватних функцій

router = Router()

def clean_phone_number(phone: str) -> str:
    """Очищує номер телефону до формату Poster POS (напр., +380991234567)."""
    cleaned = re.sub(r'\D', '', phone)
    
    if len(cleaned) == 10 and cleaned.startswith('0'):
        return f"+38{cleaned}"
    elif len(cleaned) == 12 and cleaned.startswith('380'):
        return f"+{cleaned}"
    
    return phone


# --- Приватні функції для відображення UI ---

async def _show_profile_menu(callback: CallbackQuery, user_repo: UserRepository, loyalty_service: PosterLoyaltyService, state: FSMContext) -> None:
    """Показує користувачу головний екран профілю."""
    user_id = callback.from_user.id
    user_db = await user_repo.get_by_id(user_id)
    
    await state.set_state(ProfileState.main)
    
    phone_status = "Не прив'язано ❌"
    loyalty_balance = "Невідомо"
    is_phone_attached = False

    if user_db.phone_number:
        poster_info = await loyalty_service.get_client_info(user_db.phone_number)
        
        if poster_info and poster_info.get("is_registered"):
            phone_status = f"Прив'язано: {user_db.phone_number} ✅"
            loyalty_balance = f"**{poster_info['bonus_balance']}**"
            is_phone_attached = True
        else:
            phone_status = f"Прив'язано: {user_db.phone_number} (не знайдено в Poster ⚠️)"
            is_phone_attached = True
            
    
    profile_text = (
        "⭐ **Ваш Профіль PerkUP**\n\n"
        f"**👤 Ім'я**: {user_db.name or callback.from_user.first_name}\n"
        f"**🆔 Telegram ID**: `{user_db.id}`\n\n"
        f"**📞 Статус телефону**: {phone_status}\n"
        f"**💰 Бонусний баланс**: {loyalty_balance} балів\n\n"
        "Використовуйте бонуси для оплати до 50% вартості замовлення!"
    )
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=get_profile_main_keyboard(is_phone_attached),
        parse_mode="Markdown"
    )
    # Ми не відповідаємо на callback.answer тут, оскільки це приватна функція


# --- ХЕНДЛЕРИ ПРОФІЛЮ ---

# --- 1. Обробник: Перейти до Профілю (show_profile) ---
@router.callback_query(F.data == "show_profile")
async def show_profile_handler(
    callback: CallbackQuery,
    user_repo: UserRepository,
    loyalty_service: PosterLoyaltyService,
    state: FSMContext
) -> None:
    """Показує головний екран профілю користувача."""
    await _show_profile_menu(callback, user_repo, loyalty_service, state)
    await callback.answer()


# --- 2. Обробник: Запит на Прив'язку Телефону ---
@router.callback_query(F.data == "attach_phone", ProfileState.main)
async def request_phone_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Запитує у користувача номер телефону через спеціальну клавіатуру."""
    
    await state.set_state(ProfileState.waiting_for_phone)
    
    await callback.message.edit_text(
        "📞 **Прив'язка Номера Телефону**\n\n"
        "Для доступу до бонусів Poster POS, будь ласка, **натисніть кнопку** "
        "нижче, щоб поділитися своїм контактом. Це безпечно.",
        reply_markup=get_request_contact_reply_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


# --- 3. Обробник: Отримання Номера Телефону (через кнопку) ---
@router.message(F.contact, ProfileState.waiting_for_phone)
async def receive_contact_handler(
    message: Message,
    user_repo: UserRepository,
    loyalty_service: PosterLoyaltyService,
    state: FSMContext
) -> None:
    """Отримує номер телефону, зберігає його та повертає до профілю."""
    
    phone_number = message.contact.phone_number
    user_id = message.from_user.id
    
    cleaned_phone = clean_phone_number(phone_number)
    
    user_db = await user_repo.get_by_id(user_id)
    user_db.phone_number = cleaned_phone
    await user_repo.session.commit()
    
    # UI/UX: Повернення до профілю
    await message.answer(
        "✅ Номер телефону успішно збережено!",
        reply_markup=get_remove_reply_keyboard() 
    )
    
    # Імітуємо CallbackQuery для повторного відображення профілю
    await state.set_state(ProfileState.main) 
    await _show_profile_menu(CallbackQuery(id='temp', from_user=message.from_user, chat_instance='temp', data='show_profile', message=message), user_repo, loyalty_service, state)
    
    
# --- 4. Обробник: Видалення Номера Телефону ---
@router.callback_query(F.data == "remove_phone", ProfileState.main)
async def remove_phone_handler(
    callback: CallbackQuery,
    user_repo: UserRepository,
    loyalty_service: PosterLoyaltyService,
    state: FSMContext
) -> None:
    """Видаляє номер телефону з профілю користувача."""
    user_id = callback.from_user.id
    user_db = await user_repo.get_by_id(user_id)
    
    if user_db.phone_number:
        user_db.phone_number = None
        await user_repo.session.commit()
        await callback.answer("Номер телефону видалено!")
    
    await _show_profile_menu(callback, user_repo, loyalty_service, state)


# --- 5. Обробник: Зміна Локації ---
@router.callback_query(F.data == "change_location", ProfileState.main)
async def change_location_from_profile_handler(
    callback: CallbackQuery,
    location_repo: LocationRepository,
    state: FSMContext
) -> None:
    """Перехід до вибору локації."""
    
    locations_db = await location_repo.get_active_locations()
    
    await callback.message.edit_text(
        "📍 **Зміна Локації**\n\nБудь ласка, виберіть нову локацію:",
        reply_markup=_show_location_selection(locations_db),
        parse_mode="Markdown"
    )
    
    # Встановлюємо FSM-стан, щоб обробник start.py міг обробити відповідь
    # Використовуємо OrderState.in_menu як спільний стан для вибору локації
    await state.set_state(OrderState.in_menu) 
    await callback.answer("Вибір локації")


# --- 6. Обробник: Назад до Головного Меню (з Профілю) ---
@router.callback_query(F.data == "back_to_main", ProfileState.main)
async def back_to_main_from_profile_handler(
    callback: CallbackQuery,
    user_repo: UserRepository,
    location_repo: LocationRepository,
    state: FSMContext
) -> None:
    """Повернення до головного меню."""

    await state.clear()
    
    user_db = await user_repo.get_by_id(callback.from_user.id)
    
    if user_db.preferred_location_id:
        location = await location_repo.get_by_id(user_db.preferred_location_id)
        location_name = location.name if location else "Невідома локація"
        await _show_main_menu(callback, user_db, location_name)
    else:
        await callback.message.edit_text("Будь ласка, почніть з команди /start, щоб вибрати локацію.")
        
    await callback.answer("Повернення до головного меню.")
