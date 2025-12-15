"""User schemas"""

from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    """Base user schema"""
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    telegram_id: int
    photo_url: str | None = None


class UserUpdate(BaseModel):
    """Schema for updating user settings"""
    language_code: str | None = None
    notifications_enabled: bool | None = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    telegram_id: int
    photo_url: str | None = None
    points: int
    experience: int
    level: int
    total_checkins: int
    total_games_played: int
    best_game_score: int
    referral_code: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    """Extended user profile response"""
    level_name: str
    level_bonus: float
    next_level_xp: int
    xp_to_next_level: int
    notifications_enabled: bool
    language_code: str

    @classmethod
    def from_user(cls, user) -> "UserProfileResponse":
        """Create profile response from user model"""
        level_names = {
            1: "Новачок",
            2: "Кавоман",
            3: "Бариста-учень",
            4: "Бариста",
            5: "Старший бариста",
            6: "Майстер",
            7: "Експерт",
            8: "Гуру кави",
            9: "Легенда",
            10: "Coffee King",
        }
        level_thresholds = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500]

        next_level_xp = level_thresholds[min(user.level, 9)]
        xp_to_next = max(0, next_level_xp - user.experience)

        return cls(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            photo_url=user.photo_url,
            points=user.points,
            experience=user.experience,
            level=user.level,
            total_checkins=user.total_checkins,
            total_games_played=user.total_games_played,
            best_game_score=user.best_game_score,
            referral_code=user.referral_code,
            created_at=user.created_at,
            level_name=level_names.get(user.level, "Новачок"),
            level_bonus=user.get_level_bonus(),
            next_level_xp=next_level_xp,
            xp_to_next_level=xp_to_next,
            notifications_enabled=user.notifications_enabled,
            language_code=user.language_code,
        )
