"""Leaderboard model"""

from datetime import datetime, date
from sqlalchemy import Integer, String, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Leaderboard(Base):
    """Leaderboard model - aggregated scores by period"""

    __tablename__ = "leaderboard"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    game_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("games.id"), nullable=True, index=True)

    # Period
    period_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # daily, weekly, monthly, all_time
    period_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Stats
    total_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    best_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    games_played: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Rank (calculated)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("user_id", "game_id", "period_type", "period_date", name="uq_leaderboard_entry"),
    )

    # Relationships
    user = relationship("User")
    game = relationship("Game")

    def __repr__(self) -> str:
        return f"<Leaderboard {self.id} (User {self.user_id}, {self.period_type}, Rank {self.rank})>"
