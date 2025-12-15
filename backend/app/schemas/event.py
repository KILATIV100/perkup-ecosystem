"""Event schemas"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class EventBase(BaseModel):
    """Base event schema"""
    title: str
    slug: str
    description: str | None = None
    short_description: str | None = None
    event_type: str  # promo, tournament, offline, challenge


class EventCreate(EventBase):
    """Schema for creating an event"""
    starts_at: datetime
    ends_at: datetime
    requirements: dict = {}
    rewards: dict = {}
    max_participants: int | None = None
    location_id: int | None = None
    cover_image: str | None = None
    is_featured: bool = False


class EventResponse(EventBase):
    """Event response schema"""
    id: UUID
    starts_at: datetime
    ends_at: datetime
    requirements: dict
    rewards: dict
    max_participants: int | None = None
    current_participants: int
    location_id: int | None = None
    cover_image: str | None = None
    status: str
    is_featured: bool
    is_active: bool
    is_upcoming: bool
    is_past: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """List of events response"""
    events: list[EventResponse]
    total: int


class EventParticipantResponse(BaseModel):
    """Event participant response schema"""
    id: UUID
    event_id: UUID
    user_id: int
    progress: dict
    progress_percentage: int
    status: str
    rewards_claimed: bool
    registered_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class JoinEventResponse(BaseModel):
    """Response when joining an event"""
    success: bool = True
    participation: EventParticipantResponse


class EventProgressResponse(BaseModel):
    """Event progress response"""
    participation: EventParticipantResponse
    event: EventResponse
