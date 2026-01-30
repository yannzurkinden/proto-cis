"""Skill repository for database operations."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.skill import BeneficiarySkill, Skill, Training
from app.repositories.base import BaseRepository


class SkillRepository(BaseRepository[Skill]):
    """Repository for Skill model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Skill)

    async def get_all_active(self) -> list[Skill]:
        """Get all active skills ordered by sort_order."""
        result = await self.db.execute(
            select(Skill)
            .where(Skill.is_active == True)
            .order_by(Skill.sort_order)
        )
        return list(result.scalars().all())

    async def get_by_category(self, category: str) -> list[Skill]:
        """Get skills by category."""
        result = await self.db.execute(
            select(Skill)
            .where(Skill.category == category)
            .where(Skill.is_active == True)
            .order_by(Skill.sort_order)
        )
        return list(result.scalars().all())

    # BeneficiarySkill operations

    async def get_beneficiary_skills(self, beneficiary_id: int) -> list[BeneficiarySkill]:
        """Get all skill evaluations for a beneficiary."""
        result = await self.db.execute(
            select(BeneficiarySkill)
            .options(selectinload(BeneficiarySkill.skill))
            .where(BeneficiarySkill.beneficiary_id == beneficiary_id)
            .order_by(BeneficiarySkill.evaluation_date.desc())
        )
        return list(result.scalars().all())

    async def evaluate_skill(
        self,
        beneficiary_id: int,
        skill_id: int,
        level: str,
        evaluated_by: int,
        comments: str | None = None,
    ) -> BeneficiarySkill:
        """Create or update a skill evaluation for a beneficiary (upsert)."""
        existing = await self.get_beneficiary_skill(beneficiary_id, skill_id)

        if existing:
            existing.level = level
            existing.evaluated_by = evaluated_by
            existing.evaluation_date = date.today()
            existing.comments = comments
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            skill_eval = BeneficiarySkill(
                beneficiary_id=beneficiary_id,
                skill_id=skill_id,
                level=level,
                evaluated_by=evaluated_by,
                evaluation_date=date.today(),
                comments=comments,
            )
            self.db.add(skill_eval)
            await self.db.flush()
            await self.db.refresh(skill_eval)
            return skill_eval

    async def get_beneficiary_skill(
        self,
        beneficiary_id: int,
        skill_id: int,
    ) -> BeneficiarySkill | None:
        """Get a specific skill evaluation for a beneficiary."""
        result = await self.db.execute(
            select(BeneficiarySkill)
            .where(BeneficiarySkill.beneficiary_id == beneficiary_id)
            .where(BeneficiarySkill.skill_id == skill_id)
        )
        return result.scalar_one_or_none()

    # Training operations

    async def get_trainings(self, beneficiary_id: int) -> list[Training]:
        """Get all trainings for a beneficiary."""
        result = await self.db.execute(
            select(Training)
            .where(Training.beneficiary_id == beneficiary_id)
            .order_by(Training.training_date.desc())
        )
        return list(result.scalars().all())

    async def get_training_by_id(self, training_id: int) -> Training | None:
        """Get a training by ID."""
        result = await self.db.execute(
            select(Training).where(Training.id == training_id)
        )
        return result.scalar_one_or_none()

    async def create_training(self, beneficiary_id: int, data: dict) -> Training:
        """Create a training for a beneficiary."""
        training = Training(beneficiary_id=beneficiary_id, **data)
        self.db.add(training)
        await self.db.flush()
        await self.db.refresh(training)
        return training

    async def update_training(self, training: Training, data: dict) -> Training:
        """Update a training."""
        for key, value in data.items():
            if hasattr(training, key) and value is not None:
                setattr(training, key, value)
        await self.db.flush()
        await self.db.refresh(training)
        return training

    async def delete_training(self, training: Training) -> None:
        """Delete a training."""
        await self.db.delete(training)
        await self.db.flush()
