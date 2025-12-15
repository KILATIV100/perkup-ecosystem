"""User model"""

from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    """User model - stores Telegram user data and loyalty information"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Loyalty data
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_checkins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_games_played: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    best_game_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Settings
    language_code: Mapped[str] = mapped_column(String(10), default="uk", nullable=False)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Referral
    referral_code: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    referred_by_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Timestamps
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    checkins = relationship("Checkin", back_populates="user", lazy="dynamic")
    game_sessions = relationship("GameSession", back_populates="user", lazy="dynamic")
    event_participations = relationship("EventParticipant", back_populates="user", lazy="dynamic")
    achievements = relationship("UserAchievement", back_populates="user", lazy="dynamic")
    notifications = relationship("Notification", back_populates="user", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User {self.id} (@{self.username})>"

    @property
    def display_name(self) -> str:
        """Get display name (first_name or username)"""
        return self.first_name or self.username or f"User {self.telegram_id}"

    def calculate_level(self) -> int:
        """Calculate user level based on experience"""
        level_thresholds = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500]
        for i, threshold in enumerate(level_thresholds):
            if self.experience < threshold:
                return i
        return 10

    def get_level_bonus(self) -> float:
        """Get points bonus multiplier based on level"""
        bonuses = {
            1: 0, 2: 0.05, 3: 0.10, 4: 0.15, 5: 0.20,
            6: 0.25, 7: 0.30, 8: 0.35, 9: 0.40, 10: 0.50
        }
        return bonuses.get(self.level, 0)
