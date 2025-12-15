"""Game models"""

import uuid
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Text, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Game(Base):
    """Game model - available games"""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Config
    max_points_per_game: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    points_conversion_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0.02, nullable=False)

    # Media
    icon_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    sessions = relationship("GameSession", back_populates="game", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Game {self.id} ({self.name})>"


class GameSession(Base):
    """GameSession model - individual game plays"""

    __tablename__ = "game_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False, index=True)

    # Results
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Rewards
    points_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    experience_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Platform
    platform: Mapped[str] = mapped_column(String(20), default="tma", nullable=False)

    # Status
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="game_sessions")
    game = relationship("Game", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<GameSession {self.id} (User {self.user_id}, Game {self.game_id}, Score {self.score})>"
