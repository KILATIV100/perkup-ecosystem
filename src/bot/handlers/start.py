# src/bot/handlers/start.py

from aiogram import Router
from aiogram.filters import CommandStart, Text
from aiogram.types import Message, CallbackQuery
from loguru import logger
from src.app.repositories.user_repo import UserRepository
from src.app.repositories.location_repo import LocationRepository
from src.app.domain.models import LocationDTO
from src.db.models import User # Потрібно для Pydantic from_attributes
from src.bot.keyboards.location_menu import get_location_selection_keyboard
from src.bot.keyboards.main_menu import get_main_menu_keyboard

router = Router()

# --- Приватна функція для відображення головного меню ---
async def _show_main_menu(message_or_callback: Message | CallbackQuery, user: User, location_name: str) -> None:
    """Показує головне меню бота (викликається, коли локація вже вибрана)."""
    
    # Визначаємо, звідки прийшов запит
    target_message = message_or_callback.message if isinstance(message_or_callback, CallbackQuery) else message_or_callback
    user_name = user.name or target_message.from_user.first_name
    
    welcome_text = (
        f"👋 Вітаю, **{user_name}**! \n\n"
        f"Ваша поточна локація: **{location_name}**\n\n"
        "Обери дію, щоб зробити замовлення, переглянути бонуси або профіль:"
    )
    
    await target_message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown" 
    )


# --- 1. Обробник команди /start ---
@router.message(CommandStart())
async def command_start_handler(
    message: Message, 
    user_repo: UserRepository,
    location_repo: LocationRepository
) -> None:
    """
    Обробляє команду /start.
    1. Реєструє/ідентифікує користувача.
    2. Вимагає вибору локації, якщо вона не встановлена.
    """
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name

    # 1. Ідентифікація користувача (DDD: UserRepository)
    user_db, is_new = await user_repo.get_or_create_user(
        user_id=user_id, 
        user_name=user_full_name
    )
    await user_repo.session.commit() # Фіксуємо створення, якщо воно відбулося
    
    # 2. Перевірка локації
    if user_db.preferred_location_id is None:
        logger.info(f"User {user_id} is new or needs location selection.")
        
        # 3. Якщо локації немає, пропонуємо вибрати
        locations_db = await location_repo.get_active_locations()
        
        # Мапуємо ORM-об'єкти на DTO для чистоти
        locations_dto = [LocationDTO.model_validate(loc) for loc in locations_db]
        
        if not locations_dto:
             await message.answer(
                "На жаль, наразі немає доступних локацій. Спробуйте пізніше."
             )
             return

        await message.answer(
            "📍 **Будь ласка, виберіть локацію PerkUP**, в якій ви плануєте робити замовлення:",
            reply_markup=get_location_selection_keyboard(locations_dto),
            parse_mode="Markdown"
        )
    else:
        # 4. Якщо локація є, показуємо головне меню
        location = await location_repo.get_by_id(user_db.preferred_location_id)
        location_name = location.name if location else "Невідома локація"
        await _show_main_menu(message, user_db, location_name)
        

# --- 2. Обробник Callback Query для вибору локації ---
@router.callback_query(Text(startswith="select_loc:"))
async def select_location_callback(
    callback: CallbackQuery,
    user_repo: UserRepository,
    location_repo: LocationRepository
) -> None:
    """
    Обробляє вибір локації користувачем, оновлює його профіль та показує головне меню.
    """
    location_id_str = callback.data.split(":")[1]
    location_id = int(location_id_str)
    
    # 1. Оновлення даних користувача
    user_db = await user_repo.get_by_id(callback.from_user.id)
    location_db = await location_repo.get_by_id(location_id)
    
    if user_db and location_db:
        # Оновлюємо модель у сесії
        user_db.preferred_location_id = location_id
        
        # Фіксуємо зміни в базі даних
        await user_repo.session.commit()
        
        # 2. Зміна повідомлення (UI/UX)
        await callback.message.edit_text(
            f"✅ Ваша локація встановлена: **{location_db.name}**! \n\n"
            "Тепер ви можете перейти до формування замовлення.",
            parse_mode="Markdown"
        )
        # 3. Відразу показуємо головне меню новим повідомленням
        await _show_main_menu(callback, user_db, location_db.name)
        
        await callback.answer(f"Локація змінена на {location_db.name}")
        logger.info(f"User {callback.from_user.id} set location to {location_id}")
    else:
        await callback.answer("Помилка: Не вдалося знайти користувача або локацію.")
        logger.error(f"Error updating location for user {callback.from_user.id}")
