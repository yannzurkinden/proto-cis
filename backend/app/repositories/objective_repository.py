"""Objective repository for database operations."""

from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.objective import Objective, ObjectiveIndicator, Action
from app.models.beneficiary import Beneficiary
from app.repositories.base import BaseRepository


class ObjectiveRepository(BaseRepository[Objective]):
    """Repository for Objective model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Objective)

    async def get_by_id_with_relations(self, id: int) -> Optional[Objective]:
        """Get objective by ID with all relations loaded."""
        result = await self.db.execute(
            select(Objective)
            .options(
                selectinload(Objective.indicators),
                selectinload(Objective.actions),
                selectinload(Objective.beneficiary),
            )
            .where(Objective.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all_filtered(
        self,
        skip: int = 0,
        limit: int = 20,
        beneficiary_id: Optional[int] = None,
        pai_id: Optional[int] = None,
        status: Optional[str] = None,
        objective_type: Optional[str] = None,
        term: Optional[str] = None,
        overdue: Optional[bool] = None,
        unit_id: Optional[int] = None,
    ) -> tuple[List[Objective], int]:
        """Get all objectives with filtering and pagination."""
        query = (
            select(Objective)
            .options(
                selectinload(Objective.indicators),
                selectinload(Objective.actions),
                selectinload(Objective.beneficiary).selectinload(Beneficiary.unit),
            )
        )

        # Apply filters
        if beneficiary_id:
            query = query.where(Objective.beneficiary_id == beneficiary_id)
        if pai_id:
            query = query.where(Objective.pai_id == pai_id)
        if status:
            query = query.where(Objective.status == status)
        if objective_type:
            query = query.where(Objective.objective_type == objective_type)
        if term:
            query = query.where(Objective.term == term)
        if overdue:
            query = query.where(
                and_(
                    Objective.due_date < date.today(),
                    Objective.status.in_(["pending", "in_progress"]),
                )
            )
        if unit_id:
            query = query.join(Beneficiary).where(Beneficiary.unit_id == unit_id)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginated query
        query = query.offset(skip).limit(limit).order_by(Objective.due_date, Objective.created_at)
        result = await self.db.execute(query)
        objectives = list(result.scalars().all())

        return objectives, total

    async def get_by_beneficiary(
        self,
        beneficiary_id: int,
        status: Optional[str] = None,
    ) -> List[Objective]:
        """Get all objectives for a beneficiary."""
        query = (
            select(Objective)
            .options(
                selectinload(Objective.indicators),
                selectinload(Objective.actions),
            )
            .where(Objective.beneficiary_id == beneficiary_id)
        )

        if status:
            query = query.where(Objective.status == status)

        query = query.order_by(Objective.due_date, Objective.created_at)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_overdue_objectives(
        self,
        unit_id: Optional[int] = None,
        referent_id: Optional[int] = None,
    ) -> List[Objective]:
        """Get overdue objectives."""
        query = (
            select(Objective)
            .options(selectinload(Objective.beneficiary))
            .where(Objective.due_date < date.today())
            .where(Objective.status.in_(["pending", "in_progress"]))
        )

        if unit_id or referent_id:
            query = query.join(Beneficiary)
            if unit_id:
                query = query.where(Beneficiary.unit_id == unit_id)
            if referent_id:
                query = query.where(Beneficiary.referent_id == referent_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_objective(
        self,
        data: dict,
        indicators: Optional[List[dict]] = None,
        actions: Optional[List[dict]] = None,
        created_by: int = None,
    ) -> Objective:
        """Create a new objective with indicators and actions."""
        objective = Objective(created_by=created_by, **data)
        self.db.add(objective)
        await self.db.flush()

        # Create indicators
        if indicators:
            for indicator_data in indicators:
                indicator = ObjectiveIndicator(
                    objective_id=objective.id,
                    **indicator_data,
                )
                self.db.add(indicator)

        # Create actions
        if actions:
            for action_data in actions:
                action = Action(
                    objective_id=objective.id,
                    **action_data,
                )
                self.db.add(action)

        await self.db.flush()
        await self.db.refresh(objective)
        return objective

    async def update_progress(
        self,
        objective: Objective,
        progress: int,
    ) -> Objective:
        """Update objective progress."""
        objective.progress = progress
        if progress == 100 and objective.status != "achieved":
            objective.status = "achieved"
        elif progress > 0 and objective.status == "pending":
            objective.status = "in_progress"

        await self.db.flush()
        await self.db.refresh(objective)
        return objective

    async def update_status(
        self,
        objective: Objective,
        status: str,
    ) -> Objective:
        """Update objective status."""
        objective.status = status
        if status == "achieved":
            objective.progress = 100

        await self.db.flush()
        await self.db.refresh(objective)
        return objective

    # Indicator operations
    async def get_indicator_by_id(self, indicator_id: int) -> Optional[ObjectiveIndicator]:
        """Get indicator by ID."""
        result = await self.db.execute(
            select(ObjectiveIndicator).where(ObjectiveIndicator.id == indicator_id)
        )
        return result.scalar_one_or_none()

    async def achieve_indicator(self, indicator: ObjectiveIndicator) -> ObjectiveIndicator:
        """Mark an indicator as achieved."""
        indicator.is_achieved = True
        indicator.achieved_at = datetime.now(timezone.utc)
        await self.db.flush()
        return indicator

    # Action operations
    async def get_action_by_id(self, action_id: int) -> Optional[Action]:
        """Get action by ID."""
        result = await self.db.execute(
            select(Action).where(Action.id == action_id)
        )
        return result.scalar_one_or_none()

    async def create_action(self, objective_id: int, data: dict) -> Action:
        """Create a new action."""
        action = Action(objective_id=objective_id, **data)
        self.db.add(action)
        await self.db.flush()
        await self.db.refresh(action)
        return action

    async def update_action(self, action: Action, data: dict) -> Action:
        """Update an action."""
        for key, value in data.items():
            if hasattr(action, key) and value is not None:
                setattr(action, key, value)
        await self.db.flush()
        await self.db.refresh(action)
        return action

    async def delete_action(self, action: Action) -> None:
        """Delete an action."""
        await self.db.delete(action)
        await self.db.flush()

    async def get_objectives_stats(
        self,
        unit_id: Optional[int] = None,
    ) -> dict:
        """Get statistics for objectives."""
        query = select(
            func.count().label("total"),
            func.count().filter(Objective.status == "pending").label("pending"),
            func.count().filter(Objective.status == "in_progress").label("in_progress"),
            func.count().filter(Objective.status == "achieved").label("achieved"),
            func.count().filter(Objective.status == "abandoned").label("abandoned"),
            func.count().filter(
                and_(
                    Objective.due_date < date.today(),
                    Objective.status.in_(["pending", "in_progress"]),
                )
            ).label("overdue"),
        )

        if unit_id:
            query = query.join(Beneficiary).where(Beneficiary.unit_id == unit_id)

        result = await self.db.execute(query)
        row = result.one()

        return {
            "total": row.total,
            "pending": row.pending,
            "in_progress": row.in_progress,
            "achieved": row.achieved,
            "abandoned": row.abandoned,
            "overdue": row.overdue,
        }
