"""Location model"""

from datetime import datetime
from sqlalchemy import Boolean, Integer, String, DateTime, Text, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Location(Base):
    """Location model - coffee shop locations"""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), default="Бровари", nullable=False)

    # Geo coordinates
    latitude: Mapped[float] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(11, 8), nullable=False)
    checkin_radius_meters: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # Details
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    working_hours: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    features: Mapped[list | None] = mapped_column(JSONB, nullable=True)  # ["wifi", "parking", "terrace"]

    # Media
    cover_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    photos: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Stats
    total_checkins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    checkins = relationship("Checkin", back_populates="location", lazy="dynamic")
    events = relationship("Event", back_populates="location", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Location {self.id} ({self.name})>"
