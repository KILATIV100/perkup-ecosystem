"""User service - business logic for user operations"""

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.helpers import generate_referral_code


class UserService:
    """Service for user-related operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID"""
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        user = User(
            telegram_id=user_data.telegram_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            photo_url=user_data.photo_url,
            referral_code=generate_referral_code(),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_or_create(self, telegram_data: dict) -> tuple[User, bool]:
        """
        Get existing user or create new one from Telegram data.

        Returns:
            Tuple of (user, is_new)
        """
        user = await self.get_by_telegram_id(telegram_data.get("id"))

        if user:
            # Update user data from Telegram
            user.username = telegram_data.get("username")
            user.first_name = telegram_data.get("first_name")
            user.last_name = telegram_data.get("last_name")
            user.photo_url = telegram_data.get("photo_url")
            user.last_active_at = datetime.utcnow()
            await self.db.flush()
            return user, False

        # Create new user
        user_create = UserCreate(
            telegram_id=telegram_data.get("id"),
            username=telegram_data.get("username"),
            first_name=telegram_data.get("first_name"),
            last_name=telegram_data.get("last_name"),
            photo_url=telegram_data.get("photo_url"),
        )
        user = await self.create(user_create)
        return user, True

    async def update(self, user: User, update_data: UserUpdate) -> User:
        """Update user settings"""
        if update_data.language_code is not None:
            user.language_code = update_data.language_code
        if update_data.notifications_enabled is not None:
            user.notifications_enabled = update_data.notifications_enabled

        user.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def add_points(self, user: User, points: int, experience: int = 0) -> User:
        """Add points and experience to user"""
        # Apply level bonus
        bonus = user.get_level_bonus()
        actual_points = int(points * (1 + bonus))

        user.points += actual_points
        user.experience += experience

        # Check for level up
        new_level = user.calculate_level()
        if new_level > user.level:
            user.level = new_level

        user.updated_at = datetime.utcnow()
        await self.db.flush()
        return user

    async def increment_checkins(self, user: User) -> User:
        """Increment user's total checkins"""
        user.total_checkins += 1
        await self.db.flush()
        return user

    async def increment_games_played(self, user: User, score: int) -> User:
        """Increment user's games played and update best score"""
        user.total_games_played += 1
        if score > user.best_game_score:
            user.best_game_score = score
        await self.db.flush()
        return user
