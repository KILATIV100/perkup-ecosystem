# src/app/repositories/product_repo.py

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.app.repositories.base_repo import BaseRepo
from src.db.models import Product, Category, Option

class ProductRepository(BaseRepo[Product]):
    """
    Репозиторій для роботи з Меню, Категоріями та Опціями.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)
        self.category_model = Category
        self.option_model = Option

    async def get_all_categories(self) -> List[Category]:
        """Отримати всі активні категорії."""
        stmt = select(self.category_model).order_by(self.category_model.id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_products_by_category(self, category_id: int) -> List[Product]:
        """Отримати всі доступні продукти певної категорії, завантажуючи їхні опції."""
        stmt = (
            select(self.model)
            .where(self.model.category_id == category_id)
            .where(self.model.is_available == True)
            # Жадібне завантаження зв'язків для уникнення N+1 проблеми
            .options(selectinload(self.model.options_links).selectinload(self.model.options_links[0].option))
            .order_by(self.model.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_product_with_options(self, product_id: int) -> Optional[Product]:
        """Отримати один продукт з усіма його опціями."""
        stmt = (
            select(self.model)
            .where(self.model.id == product_id)
            .options(selectinload(self.model.options_links).selectinload(self.model.options_links[0].option))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_options_by_ids(self, option_ids: List[int]) -> List[Option]:
        """Отримати список об'єктів Option за їхніми ID."""
        if not option_ids:
            return []
        stmt = select(self.option_model).where(self.option_model.id.in_(option_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
