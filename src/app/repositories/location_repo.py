# src/app/repositories/location_repo.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.repositories.base_repo import BaseRepo
from src.db.models import Location

class LocationRepository(BaseRepo[Location]):
    """
    Репозиторій для роботи з сутністю Локація (Location).
    Наслідує загальні CRUD-операції від BaseRepo.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(session, Location)
    
    async def get_active_locations(self) -> list[Location]:
        """Отримати список усіх активних локацій для відображення в меню."""
        stmt = select(Location).where(Location.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
