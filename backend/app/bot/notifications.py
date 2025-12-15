"""Telegram notification service"""

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from app.core.config import settings


class NotificationService:
    """Service for sending Telegram notifications"""

    def __init__(self):
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured")
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.tma_url = settings.TELEGRAM_WEBAPP_URL

    async def send_checkin_reminder(self, telegram_id: int) -> bool:
        """Send check-in reminder notification"""
        text = "☕ Давно не бачились! Зайди до нашої кав'ярні та отримай +1 бал!"

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "☕ Check-in",
                web_app=WebAppInfo(url=f"{self.tma_url}/checkin")
            )
        ]])

        return await self._send_message(telegram_id, text, keyboard)

    async def send_tournament_start(
        self,
        telegram_id: int,
        tournament_name: str,
        prize_description: str
    ) -> bool:
        """Send tournament start notification"""
        text = f"""
🏆 *Новий турнір почався!*

*{tournament_name}*

🎁 Призи: {prize_description}

Візьми участь та вигравай круті нагороди!
"""
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "🎮 Взяти участь",
                web_app=WebAppInfo(url=f"{self.tma_url}/games")
            )
        ]])

        return await self._send_message(telegram_id, text, keyboard, parse_mode="Markdown")

    async def send_tournament_end(
        self,
        telegram_id: int,
        tournament_name: str,
        position: int,
        points_won: int
    ) -> bool:
        """Send tournament end notification"""
        if position <= 3:
            emoji = ["🥇", "🥈", "🥉"][position - 1]
            congrats = f"Вітаємо! Ти зайняв {emoji} {position} місце"
        else:
            emoji = "🎊"
            congrats = f"Ти зайняв {position} місце"

        text = f"""
{emoji} *Турнір завершено!*

*{tournament_name}*

{congrats} та отримав *{points_won} балів*!

Дякуємо за участь!
"""
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "🏆 Результати",
                web_app=WebAppInfo(url=f"{self.tma_url}/leaderboard")
            )
        ]])

        return await self._send_message(telegram_id, text, keyboard, parse_mode="Markdown")

    async def send_new_event(
        self,
        telegram_id: int,
        event_title: str,
        event_description: str,
        event_slug: str
    ) -> bool:
        """Send new event notification"""
        text = f"""
🎉 *Новий івент!*

*{event_title}*

{event_description}

Не пропусти!
"""
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "🎉 Детальніше",
                web_app=WebAppInfo(url=f"{self.tma_url}/events/{event_slug}")
            )
        ]])

        return await self._send_message(telegram_id, text, keyboard, parse_mode="Markdown")

    async def send_reward_available(
        self,
        telegram_id: int,
        reward_description: str
    ) -> bool:
        """Send reward available notification"""
        text = f"""
🎁 *У тебе є нагорода!*

{reward_description}

Забери її в додатку!
"""
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "🎁 Забрати нагороду",
                web_app=WebAppInfo(url=f"{self.tma_url}/profile")
            )
        ]])

        return await self._send_message(telegram_id, text, keyboard, parse_mode="Markdown")

    async def send_level_up(
        self,
        telegram_id: int,
        new_level: int,
        level_name: str
    ) -> bool:
        """Send level up notification"""
        text = f"""
⭐ *Вітаємо з новим рівнем!*

Тепер ти *Level {new_level} — {level_name}*!

Продовжуй в тому ж дусі!
"""
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "👤 Мій профіль",
                web_app=WebAppInfo(url=f"{self.tma_url}/profile")
            )
        ]])

        return await self._send_message(telegram_id, text, keyboard, parse_mode="Markdown")

    async def send_checkin_success(
        self,
        telegram_id: int,
        location_name: str,
        points_earned: int,
        total_points: int
    ) -> bool:
        """Send check-in success notification"""
        text = f"""
✅ *Check-in успішний!*

📍 {location_name}
💰 +{points_earned} балів

Твій баланс: *{total_points} балів*
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🎮 Зіграти в гру",
                web_app=WebAppInfo(url=f"{self.tma_url}/games")
            )],
            [InlineKeyboardButton(
                "📊 Мій профіль",
                web_app=WebAppInfo(url=f"{self.tma_url}/profile")
            )]
        ])

        return await self._send_message(telegram_id, text, keyboard, parse_mode="Markdown")

    async def _send_message(
        self,
        telegram_id: int,
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
        parse_mode: str | None = None
    ) -> bool:
        """Send message to user"""
        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            print(f"Failed to send notification to {telegram_id}: {e}")
            return False
