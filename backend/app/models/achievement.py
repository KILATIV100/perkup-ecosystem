"""Achievement models"""

import uuid
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Achievement(Base):
    """Achievement model - available achievements/badges"""

    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # checkin, game, social, event, streak

    # Requirements
    requirements: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    # Example: {"type": "checkins", "count": 10} or {"type": "game_score", "min_score": 1000}

    # Rewards
    points_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    experience_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Media
    icon_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    badge_color: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Secret achievements

    # Order
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Achievement {self.id} ({self.name})>"


class UserAchievement(Base):
    """UserAchievement model - achievements earned by users"""

    __tablename__ = "user_achievements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    achievement_id: Mapped[int] = mapped_column(Integer, ForeignKey("achievements.id"), nullable=False, index=True)

    # Progress (for progressive achievements)
    progress: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Status
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    def __repr__(self) -> str:
        return f"<UserAchievement {self.id} (User {self.user_id}, Achievement {self.achievement_id})>"
