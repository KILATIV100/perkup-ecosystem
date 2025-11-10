# src/bot/handlers/info.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, Location
from loguru import logger
from src.app.repositories.location_repo import LocationRepository
from src.app.domain.models import LocationDTO
from src.bot.keyboards.info_kb import get_locations_keyboard, get_news_keyboard

router = Router()

# --- 1. Обробник: Відображення Локацій ---
@router.callback_query(F.data == "show_locations")
async def show_locations_handler(
    callback: CallbackQuery,
    location_repo: LocationRepository
) -> None:
    """
    Показує користувачеві список усіх локацій з можливістю перейти на карту.
    """
    # 1. Отримання активних локацій
    locations_db = await location_repo.get_active_locations()
    locations_dto = [LocationDTO.model_validate(loc) for loc in locations_db]

    if not locations_dto:
        await callback.answer("На жаль, інформація про локації тимчасово недоступна.")
        return
        
    # 2. Формування тексту та клавіатури
    locations_text = (
        "🗺️ **Наші Локації PerkUP**\n\n"
        "Ви можете відвідати нас у цих точках. Для навігації натисніть кнопку з назвою локації "
        "(відкриється Google Maps) або кнопку 'Показати на карті Telegram'."
    )
    
    await callback.message.edit_text(
        locations_text,
        reply_markup=get_locations_keyboard(locations_dto),
        parse_mode="Markdown"
    )
    await callback.answer()


# --- 2. Обробник: Надсилання Геолокації (Telegram Location) ---
@router.callback_query(F.data.startswith("send_loc:"))
async def send_location_handler(
    callback: CallbackQuery,
    location_repo: LocationRepository
) -> None:
    """
    Надсилає користувачеві об'єкт Location, який зручно відкривається в Telegram.
    """
    location_id = int(callback.data.split(":")[1])
    
    location_db = await location_repo.get_by_id(location_id)
    
    if location_db:
        # Надсилаємо Location об'єкт
        await callback.message.answer_location(
            latitude=location_db.latitude,
            longitude=location_db.longitude,
            # Додаткова інформація
            live_period=None, # Не динамічна локація
            horizontal_accuracy=50.0 # Радіус точності
        )
        await callback.answer(f"Надіслано геолокацію: {location_db.name}")
    else:
        await callback.answer("Помилка: Локацію не знайдено.")


# --- 3. Обробник: Відображення Новин та Акцій ---
@router.callback_query(F.data == "show_news")
async def show_news_handler(
    callback: CallbackQuery
) -> None:
    """
    Показує користувачеві посилання на новинні канали та соцмережі.
    """
    news_text = (
        "💡 **Новини та Акції PerkUP**\n\n"
        "Слідкуйте за свіжими акціями, новинками та змінами в меню у наших соціальних мережах:"
    )
    
    await callback.message.edit_text(
        news_text,
        reply_markup=get_news_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()
