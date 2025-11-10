# src/db/base.py

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, DateTime, mapped_column, Mapped
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовий клас для всіх SQLAlchemy ORM моделей в екосистемі PerkUP.
    Надає загальний атрибут created_at (Час створення).
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("now()") # Автоматично встановлюється базою даних
    )

    __abstract__ = True
