from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# ============= USER SCHEMAS =============
class UserBase(BaseModel):
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    points: int
    level: int
    total_checkins: int
    best_game_score: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============= LOCATION SCHEMAS =============
class LocationBase(BaseModel):
    name: str
    slug: str
    address: str
    city: str = "Бровари"
    latitude: float
    longitude: float
    radius_meters: int = 100
    description: Optional[str] = None
    is_active: bool = True

class LocationResponse(LocationBase):
    id: int
    total_checkins: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============= CHECKIN SCHEMAS =============
class CheckinCreate(BaseModel):
    location_id: int = Field(..., gt=0)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class CheckinResponse(BaseModel):
    id: int
    location_id: int
    distance_meters: int
    points_earned: int
    experience_earned: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdatedInfo(BaseModel):
    """Оновлена інформація про користувача після чекіну"""
    total_points: int
    total_checkins: int
    level: int
    level_progress: int

class CheckinSuccessResponse(BaseModel):
    success: bool
    checkin: CheckinResponse
    user_updated: UserUpdatedInfo
    message: str

# ============= AUTH SCHEMAS =============
class TelegramAuthRequest(BaseModel):
    init_data: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse