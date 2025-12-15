"""Telegram bot handlers"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from app.core.config import settings


# Web App URL
TMA_URL = settings.TELEGRAM_WEBAPP_URL


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard with WebApp buttons"""
    keyboard = [
        [InlineKeyboardButton(
            "☕ Check-in",
            web_app=WebAppInfo(url=f"{TMA_URL}/checkin")
        )],
        [InlineKeyboardButton(
            "🎮 Ігри",
            web_app=WebAppInfo(url=f"{TMA_URL}/games")
        )],
        [InlineKeyboardButton(
            "🎉 Івенти",
            web_app=WebAppInfo(url=f"{TMA_URL}/events")
        )],
        [InlineKeyboardButton(
            "🏆 Leaderboard",
            web_app=WebAppInfo(url=f"{TMA_URL}/leaderboard")
        )],
        [InlineKeyboardButton(
            "👤 Профіль",
            web_app=WebAppInfo(url=f"{TMA_URL}/profile")
        )],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user

    # Check for deep link parameter
    args = context.args
    deep_link = args[0] if args else None

    welcome_text = f"""
👋 Привіт, {user.first_name}!

Ласкаво просимо до *PerkUP* — системи лояльності для справжніх кавоманів!

🎮 *Що ти можеш робити:*
• ☕ Check-in в наших кав'ярнях
• 🎮 Грати в ігри та заробляти бали
• 🎉 Брати участь в івентах
• 🏆 Змагатися з друзями

Натисни кнопку нижче, щоб відкрити додаток!
"""

    # Handle deep links
    if deep_link:
        if deep_link.startswith("checkin_"):
            # Direct to checkin
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "☕ Зробити Check-in",
                    web_app=WebAppInfo(url=f"{TMA_URL}/checkin")
                )
            ]])
        elif deep_link.startswith("event_"):
            event_slug = deep_link.replace("event_", "")
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🎉 Перейти до івенту",
                    web_app=WebAppInfo(url=f"{TMA_URL}/events/{event_slug}")
                )
            ]])
        elif deep_link.startswith("game_"):
            game_slug = deep_link.replace("game_", "")
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "🎮 Грати",
                    web_app=WebAppInfo(url=f"{TMA_URL}/games/{game_slug}")
                )
            ]])
        elif deep_link.startswith("ref_"):
            # Referral link
            keyboard = get_main_keyboard()
            welcome_text += "\n\n🎁 Ти прийшов за запрошенням! Отримай бонусні бали!"
        else:
            keyboard = get_main_keyboard()
    else:
        keyboard = get_main_keyboard()

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """
📚 *Довідка PerkUP*

*Основні команди:*
/start - Головне меню
/balance - Перевірити баланс балів
/checkin - Зробити check-in
/play - Грати в ігри
/events - Активні івенти
/leaderboard - Таблиця лідерів
/settings - Налаштування

*Як заробити бали:*
• ☕ Check-in в кав'ярні: +1 бал
• 🎮 Грати в ігри: до 25 балів
• 🎉 Участь в івентах: різні призи
• 👥 Запросити друзів: +10 балів

*Як витратити бали:*
Обміняй бали на безкоштовні напої, знижки та мерч!

Є питання? Звертайся: @perkup_support
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /balance command"""
    # This would need to fetch from database
    # For now, show a button to open the app
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "👤 Переглянути профіль",
            web_app=WebAppInfo(url=f"{TMA_URL}/profile")
        )
    ]])

    await update.message.reply_text(
        "💰 Перевір свій баланс та статистику в додатку:",
        reply_markup=keyboard
    )


async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /checkin command"""
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "☕ Check-in",
            web_app=WebAppInfo(url=f"{TMA_URL}/checkin")
        )
    ]])

    await update.message.reply_text(
        "📍 Натисни кнопку, щоб зробити check-in у найближчій кав'ярні!",
        reply_markup=keyboard
    )


async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /play command"""
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🎮 Вибрати гру",
            web_app=WebAppInfo(url=f"{TMA_URL}/games")
        )
    ]])

    await update.message.reply_text(
        "🎮 Обери гру та заробляй бали!",
        reply_markup=keyboard
    )


async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /events command"""
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🎉 Переглянути івенти",
            web_app=WebAppInfo(url=f"{TMA_URL}/events")
        )
    ]])

    await update.message.reply_text(
        "🎉 Дізнайся про активні івенти та акції!",
        reply_markup=keyboard
    )


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /leaderboard command"""
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🏆 Leaderboard",
            web_app=WebAppInfo(url=f"{TMA_URL}/leaderboard")
        )
    ]])

    await update.message.reply_text(
        "🏆 Переглянь таблицю лідерів та свою позицію!",
        reply_markup=keyboard
    )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command"""
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "⚙️ Налаштування",
            web_app=WebAppInfo(url=f"{TMA_URL}/settings")
        )
    ]])

    await update.message.reply_text(
        "⚙️ Налаштуй свій профіль та сповіщення:",
        reply_markup=keyboard
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands"""
    await update.message.reply_text(
        "🤔 Не розумію цю команду. Скористайся /help для довідки."
    )


def create_bot_application() -> Application:
    """Create and configure bot application"""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured")

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("checkin", checkin_command))
    application.add_handler(CommandHandler("play", play_command))
    application.add_handler(CommandHandler("events", events_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(CommandHandler("settings", settings_command))

    # Handle unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    return application
