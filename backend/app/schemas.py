from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LocationBase(BaseModel):
    name: str
    slug: str
    address: str
    city: str = "Бровари"
    latitude: float
    longitude: float
    radius_meters: int = 100
    description: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True