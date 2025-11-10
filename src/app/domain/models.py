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

class CategoryDTO(BaseModel):
    """DTO для Категорії меню."""
    id: int
    name: str

    class Config:
        from_attributes = True

class OptionDTO(BaseModel):
    """DTO для опції товару (модифікатора)."""
    id: int
    name: str
    extra_cost: float = 0.00
    option_group: str

    class Config:
        from_attributes = True

class ProductDTO(BaseModel):
    """Базовий DTO для Товару/Напою з меню."""
    id: int
    name: str
    description: Optional[str] = None
    base_price: float
    category_id: int
    is_available: bool

    class Config:
        from_attributes = True
        
class ConfigurableProductDTO(ProductDTO):
    """DTO для Товару з його доступними опціями."""
    available_options: List[OptionDTO] = Field(default_factory=list) 

# --- Cart/Order DTOs (Для FSM контексту) ---

class CartItemDTO(BaseModel):
    """Одиниця товару в кошику з вибраними опціями."""
    product_id: int
    product_name: str
    quantity: int = 1
    unit_price: float # Базова ціна + вартість вибраних опцій
    selected_options: List[OptionDTO] = Field(default_factory=list)

class ShoppingCartDTO(BaseModel):
    """DTO, що представляє поточний кошик користувача."""
    location_id: int = Field(..., description="ID локації, для якої робиться замовлення.")
    items: List[CartItemDTO] = Field(default_factory=list)
    total_amount: float = 0.00
    
    def calculate_total(self) -> float:
        """Перераховує загальну суму кошика."""
        self.total_amount = sum(item.unit_price * item.quantity for item in self.items)
        return self.total_amount
