"""Checkin model"""

from datetime import datetime, date
from sqlalchemy import BigInteger, Integer, DateTime, Date, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Checkin(Base):
    """Checkin model - user check-ins at locations"""

    __tablename__ = "checkins"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False, index=True)

    # Geo verification
    user_latitude: Mapped[float | None] = mapped_column(Numeric(10, 8), nullable=True)
    user_longitude: Mapped[float | None] = mapped_column(Numeric(11, 8), nullable=True)
    distance_meters: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Rewards
    points_earned: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    experience_earned: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # Timestamps
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Prevent duplicate checkins per day per location
    __table_args__ = (
        UniqueConstraint("user_id", "location_id", "checkin_date", name="uq_user_location_date"),
    )

    # Relationships
    user = relationship("User", back_populates="checkins")
    location = relationship("Location", back_populates="checkins")

    def __repr__(self) -> str:
        return f"<Checkin {self.id} (User {self.user_id} at Location {self.location_id})>"
