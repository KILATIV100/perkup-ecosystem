# src/bot/handlers/start.py

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from src.bot.keyboards.main_menu import get_main_menu_keyboard

# Створення роутера для обробників
router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обробляє команду /start.
    Це наша головна точка входу та демонстрація UI/UX.
    """
    user_name = message.from_user.full_name
    
    # Сучасний вітальний текст
    welcome_text = (
        f"👋 Вітаю, **{user_name}**, у **PerkUP Нова Екосистема**! \n\n"
        "Я твій особистий помічник для управління та отримання **Перків** (бонусів, нагород).\n\n"
        "Обери дію в меню нижче:"
    )
    
    # Надсилаємо повідомлення з клавіатурою
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown" # Використовуємо Markdown для виділення тексту
    )
