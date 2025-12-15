"""Location schemas"""

from datetime import datetime
from pydantic import BaseModel


class LocationBase(BaseModel):
    """Base location schema"""
    name: str
    address: str
    city: str = "Бровари"
    latitude: float
    longitude: float


class LocationCreate(LocationBase):
    """Schema for creating a location"""
    slug: str
    description: str | None = None
    working_hours: dict | None = None
    features: list[str] | None = None
    cover_image: str | None = None
    checkin_radius_meters: int = 100


class LocationResponse(LocationBase):
    """Location response schema"""
    id: int
    slug: str
    description: str | None = None
    working_hours: dict | None = None
    features: list[str] | None = None
    cover_image: str | None = None
    photos: list[str] | None = None
    checkin_radius_meters: int
    total_checkins: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LocationListResponse(BaseModel):
    """List of locations response"""
    locations: list[LocationResponse]
    total: int
