# src/db/models.py

from typing import List
# --- ВИПРАВЛЕНО: Додано DateTime для використання як типу колонок SQLAlchemy ---
from sqlalchemy import BigInteger, Boolean, ForeignKey, Numeric, Text, String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from src.db.base import Base


# --- Допоміжна таблиця для зв'язку "Багато-до-Багатьох" (Products <-> Options) ---
class ProductOptionAssociation(Base):
    """Проміжна таблиця product_options: Зв'язує товари з доступними опціями."""
    __tablename__ = "product_options"
    
    # Складений первинний ключ
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    option_id: Mapped[int] = mapped_column(ForeignKey("options.id", ondelete="CASCADE"), primary_key=True)
    
    # Зв'язки
    product: Mapped["Product"] = relationship(back_populates="options_links")
    option: Mapped["Option"] = relationship(back_populates="products_links")


# --- 1. Таблиця users (Користувачі) ---
class User(Base):
    """users: Користувачі та їхній баланс лояльності."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True) # Telegram User ID
    name: Mapped[str | None] = mapped_column(String(255), nullable=True) 
    phone_number: Mapped[str | None] = mapped_column(String(15), nullable=True)
    
    loyalty_points: Mapped[int] = mapped_column(Integer, default=0) 
    preferred_location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    
    # Зв'язки
    preferred_location: Mapped["Location"] = relationship(back_populates="users")
    orders: Mapped[List["Order"]] = relationship(back_populates="user")
    loyalty_transactions: Mapped[List["LoyaltyTransaction"]] = relationship(back_populates="user")


# --- 2. Таблиця locations (Локації) ---
class Location(Base):
    """locations: Інформація про фізичні точки продажу."""
    __tablename__ = "locations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    address: Mapped[str] = mapped_column(String(255))
    
    latitude: Mapped[float] = mapped_column(Numeric(10, 8)) # Широта
    longitude: Mapped[float] = mapped_column(Numeric(11, 8)) # Довгота
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Зв'язки
    users: Mapped[List["User"]] = relationship(back_populates="preferred_location")


# --- Допоміжна таблиця categories ---
class Category(Base):
    """categories: Розділення меню на категорії."""
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True) 
    
    products: Mapped[List["Product"]] = relationship(back_populates="category")


# --- 3. Таблиця products (Товари/Меню) ---
class Product(Base):
    """products: Основне меню кав'ярні."""
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_price: Mapped[float] = mapped_column(Numeric(6, 2))
    
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Зв'язки
    category: Mapped["Category"] = relationship(back_populates="products")
    options_links: Mapped[List["ProductOptionAssociation"]] = relationship(
        back_populates="product", cascade="all, delete-orphan" # Підтримка зв'язку Many-to-Many
    )
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")


# --- 4. Таблиця options (Опції та Модифікатори) ---
class Option(Base):
    """options: Конфігурація напоїв (розмір, сироп, молоко)."""
    __tablename__ = "options"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    extra_cost: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00)
    option_group: Mapped[str] = mapped_column(String(50)) # 'Розмір', 'Тип молока'
    
    products_links: Mapped[List["ProductOptionAssociation"]] = relationship(
        back_populates="option", cascade="all, delete-orphan"
    )


# --- 5. Таблиця orders (Замовлення) ---
class Order(Base):
    """orders: Основна таблиця для фіксації кожного замовлення."""
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id")) 
    
    status: Mapped[str] = mapped_column(String(20), default="NEW")
    payment_method: Mapped[str] = mapped_column(String(20))
    
    total_amount: Mapped[float] = mapped_column(Numeric(7, 2))
    total_paid: Mapped[float] = mapped_column(Numeric(7, 2), default=0.00)
    points_used: Mapped[int] = mapped_column(Integer, default=0)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    
    pickup_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Зв'язки
    user: Mapped["User"] = relationship(back_populates="orders")
    location: Mapped["Location"] = relationship()
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    loyalty_transaction: Mapped[List["LoyaltyTransaction"]] = relationship(back_populates="order")


# --- Деталізація замовлення: order_items ---
class OrderItem(Base):
    """order_items: Які товари, в якій кількості та з якими опціями замовлені."""
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Numeric(6, 2))
    
    # Список ID опцій (зберігаємо фіксацію стану на момент замовлення)
    selected_options: Mapped[str | None] = mapped_column(Text, nullable=True) 
    
    # Зв'язки
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


# --- 6. Таблиця loyalty_transactions (Історія Бонусів) ---
class LoyaltyTransaction(Base):
    """loyalty_transactions: Історія змін балансу бонусів для аудиту."""
    __tablename__ = "loyalty_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    
    amount: Mapped[int] = mapped_column(Integer) # +N або -N балів
    type: Mapped[str] = mapped_column(String(20)) # 'EARNED', 'SPENT', 'MANUAL_ADJUSTMENT'
    
    # Зв'язки
    user: Mapped["User"] = relationship(back_populates="loyalty_transactions")
    order: Mapped["Order"] = relationship(back_populates="loyalty_transaction")
