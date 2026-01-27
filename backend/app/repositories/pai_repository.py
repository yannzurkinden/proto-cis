"""PAI repository for database operations."""

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pai import PAI
from app.models.objective import Objective
from app.repositories.base import BaseRepository


class PAIRepository(BaseRepository[PAI]):
    """Repository for PAI model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, PAI)

    async def get_by_id_with_objectives(self, id: int) -> Optional[PAI]:
        """Get PAI by ID with objectives loaded."""
        result = await self.db.execute(
            select(PAI)
            .options(selectinload(PAI.objectives))
            .where(PAI.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_beneficiary(
        self,
        beneficiary_id: int,
        status: Optional[str] = None,
    ) -> List[PAI]:
        """Get all PAIs for a beneficiary."""
        query = (
            select(PAI)
            .options(selectinload(PAI.objectives))
            .where(PAI.beneficiary_id == beneficiary_id)
        )

        if status:
            query = query.where(PAI.status == status)

        query = query.order_by(PAI.valid_from.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_pai(self, beneficiary_id: int) -> Optional[PAI]:
        """Get the active PAI for a beneficiary."""
        result = await self.db.execute(
            select(PAI)
            .options(selectinload(PAI.objectives))
            .where(PAI.beneficiary_id == beneficiary_id)
            .where(PAI.status == "active")
            .order_by(PAI.valid_from.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_pai(
        self,
        beneficiary_id: int,
        data: dict,
        created_by: int,
    ) -> PAI:
        """Create a new PAI."""
        pai = PAI(
            beneficiary_id=beneficiary_id,
            created_by=created_by,
            **data,
        )
        self.db.add(pai)
        await self.db.flush()
        await self.db.refresh(pai)
        return pai

    async def activate_pai(self, pai: PAI) -> PAI:
        """Activate a PAI and deactivate others for the same beneficiary."""
        # Deactivate other active PAIs
        result = await self.db.execute(
            select(PAI)
            .where(PAI.beneficiary_id == pai.beneficiary_id)
            .where(PAI.status == "active")
            .where(PAI.id != pai.id)
        )
        other_pais = result.scalars().all()
        for other_pai in other_pais:
            other_pai.status = "closed"

        pai.status = "active"
        await self.db.flush()
        await self.db.refresh(pai)
        return pai

    async def close_pai(self, pai: PAI) -> PAI:
        """Close a PAI."""
        pai.status = "closed"
        await self.db.flush()
        await self.db.refresh(pai)
        return pai
