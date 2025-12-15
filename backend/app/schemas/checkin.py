"""Checkin schemas"""

from datetime import datetime, date
from pydantic import BaseModel

from app.schemas.location import LocationResponse


class CheckinCreate(BaseModel):
    """Schema for creating a checkin"""
    location_id: int
    latitude: float
    longitude: float


class CheckinResponse(BaseModel):
    """Checkin response schema"""
    id: int
    location_id: int
    location_name: str
    user_latitude: float | None = None
    user_longitude: float | None = None
    distance_meters: int | None = None
    points_earned: int
    experience_earned: int
    checkin_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class CheckinSuccessResponse(BaseModel):
    """Response after successful checkin"""
    success: bool = True
    checkin: CheckinResponse
    user_updated: dict


class CheckinHistoryResponse(BaseModel):
    """Checkin history response"""
    checkins: list[CheckinResponse]
    total: int
    page: int
    per_page: int


class CheckinError(BaseModel):
    """Checkin error response"""
    success: bool = False
    error_code: str  # too_far, cooldown_active, location_inactive
    message: str
    details: dict | None = None
