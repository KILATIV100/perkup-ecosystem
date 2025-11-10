# src/app/domain/models.py
# Pydantic моделі для чистої передачі даних між шарами (Application, Domain, Bot)

from pydantic import BaseModel, Field
from typing import List, Optional

# --- Value Objects ---
class Coordinates(BaseModel):
    """Value Object для географічних координат."""
    latitude: float = Field(..., description="Широта")
    longitude: float = Field(..., description="Довгота")

# --- Core Entities DTOs ---

class LocationDTO(BaseModel):
    """DTO для передачі даних про Локацію."""
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    is_active: bool

    class Config:
        # Дозволяємо Pydantic створювати моделі безпосередньо з ORM-об'єктів
        from_attributes = True 

class UserDTO(BaseModel):
    """DTO для передачі даних про Користувача."""
    id: int # Telegram ID
    name: Optional[str] = None
    phone_number: Optional[str] = None
    loyalty_points: int = 0
    preferred_location_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# Тут будуть додані інші DTOs: ProductDTO, OrderItemDTO, OrderDTO
