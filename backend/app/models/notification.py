"""Notification model"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Notification(Base):
    """Notification model - user notifications"""

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Content
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # checkin_reminder, tournament_start, etc.
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Action
    action_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # open_app, open_event, etc.
    action_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Delivery
    channel: Mapped[str] = mapped_column(String(20), default="telegram", nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification {self.id} ({self.type} for User {self.user_id})>"
