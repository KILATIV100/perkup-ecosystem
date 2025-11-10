# src/bot/keyboards/profile_kb.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_profile_main_keyboard(is_phone_attached: bool) -> InlineKeyboardMarkup:
    """
    Створює Inline-клавіатуру для головного меню Профілю.
    """
    builder = InlineKeyboardBuilder()

    if not is_phone_attached:
        # Критична дія: прив'язати телефон
        builder.row(
            InlineKeyboardButton(text="📞 Прив'язати Номер Телефону", callback_data="attach_phone"),
        )
    else:
        # Інформаційні дії
        builder.row(
            InlineKeyboardButton(text="🗺️ Змінити Локацію", callback_data="change_location"),
            InlineKeyboardButton(text="🗑️ Видалити номер", callback_data="remove_phone")
        )

    # Кнопка повернення
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад до Головного Меню", callback_data="back_to_main")
    )
    
    builder.adjust(1, 1)

    return builder.as_markup()


def get_request_contact_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Створює Reply-клавіатуру з кнопкою для надсилання контакту.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Поділитися номером телефону", request_contact=True)
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_remove_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Повертає звичайну клавіатуру, щоб приховати клавіатуру запиту контакту.
    """
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/menu")]], resize_keyboard=True, selective=True)
