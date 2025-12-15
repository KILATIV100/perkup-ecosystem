"""Event models"""

import uuid
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Event(Base):
    """Event model - promotions, tournaments, offline events, challenges"""

    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    short_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # promo, tournament, offline, challenge

    # Timing
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Requirements & Rewards
    requirements: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    rewards: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Participation
    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_participants: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Location (for offline events)
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("locations.id"), nullable=True)

    # Media
    cover_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    images: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)  # draft, active, completed, cancelled
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    location = relationship("Location", back_populates="events")
    participants = relationship("EventParticipant", back_populates="event", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Event {self.id} ({self.title})>"

    @property
    def is_active(self) -> bool:
        """Check if event is currently active"""
        now = datetime.utcnow()
        return self.status == "active" and self.starts_at <= now <= self.ends_at

    @property
    def is_upcoming(self) -> bool:
        """Check if event is upcoming"""
        return self.status == "active" and datetime.utcnow() < self.starts_at

    @property
    def is_past(self) -> bool:
        """Check if event has ended"""
        return datetime.utcnow() > self.ends_at


class EventParticipant(Base):
    """EventParticipant model - user participation in events"""

    __tablename__ = "event_participants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Progress
    progress: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="registered", nullable=False)  # registered, in_progress, completed, rewarded

    # Rewards
    rewards_claimed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rewards_claimed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    event = relationship("Event", back_populates="participants")
    user = relationship("User", back_populates="event_participations")

    def __repr__(self) -> str:
        return f"<EventParticipant {self.id} (Event {self.event_id}, User {self.user_id})>"
