# src/app/repositories/user_repo.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.repositories.base_repo import BaseRepo
from src.db.models import User

class UserRepository(BaseRepo[User]):
    """
    Репозиторій для роботи з сутністю Користувач (User).
    """
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_or_create_user(self, user_id: int, user_name: str | None = None) -> tuple[User, bool]:
        """
        Знаходить користувача за ID або створює нового, якщо він не існує.
        Повертає кортеж: (об'єкт User, чи був користувач створений).
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalars().first()
        
        if user:
            return user, False  # Знайдено, не створено
        
        # Створюємо нового користувача
        new_user = await self.create(id=user_id, name=user_name)
        # Ми не робимо commit тут, це відповідальність Application Service.
        
        return new_user, True # Створено
