"""Unit repository for database operations."""

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.unit import Unit
from app.repositories.base import BaseRepository


class UnitRepository(BaseRepository[Unit]):
    """Repository for Unit model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Unit)

    async def get_by_name(self, name: str) -> Optional[Unit]:
        """Get unit by name."""
        result = await self.db.execute(
            select(Unit).where(Unit.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> List[Unit]:
        """Get all active units."""
        result = await self.db.execute(
            select(Unit)
            .where(Unit.is_active == True)
            .order_by(Unit.name)
        )
        return list(result.scalars().all())

    async def get_all_filtered(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> tuple[List[Unit], int]:
        """Get all units with filtering and pagination."""
        query = select(Unit)

        if is_active is not None:
            query = query.where(Unit.is_active == is_active)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginated query
        query = query.offset(skip).limit(limit).order_by(Unit.name)
        result = await self.db.execute(query)
        units = list(result.scalars().all())

        return units, total
