# src/app/repositories/base_repo.py

from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Тип змінної (T) буде представляти ORM-модель (наприклад, User, Location)
T = TypeVar("T")

class BaseRepo(Generic[T]):
    """
    Базовий репозиторій, що надає загальні CRUD-операції
    для будь-якої моделі SQLAlchemy.
    """
    def __init__(self, session: AsyncSession, model: Type[T]):
        """
        Конструктор репозиторію.
        :param session: Асинхронна сесія SQLAlchemy.
        :param model: ORM-модель, з якою працює репозиторій.
        """
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> T | None:
        """Отримати об'єкт за його первинним ключем."""
        result = await self.session.get(self.model, id)
        return result

    async def create(self, **kwargs) -> T:
        """Створити та зберегти новий об'єкт."""
        new_obj = self.model(**kwargs)
        self.session.add(new_obj)
        # На commit() ми розраховуємо на рівні Application Service або Dispatcher,
        # але base repo повинен вміти додати об'єкт до сесії.
        return new_obj

    async def get_all(self) -> list[T]:
        """Отримати всі об'єкти моделі."""
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
