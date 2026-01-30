"""Beneficiary repository for database operations."""


from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.beneficiary import Beneficiary, BeneficiaryMedicalData, Contact, RiskBehavior
from app.repositories.base import BaseRepository


class BeneficiaryRepository(BaseRepository[Beneficiary]):
    """Repository for Beneficiary model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Beneficiary)

    async def get_by_id_with_relations(self, id: int) -> Beneficiary | None:
        """Get beneficiary by ID with all relations loaded."""
        result = await self.db.execute(
            select(Beneficiary)
            .options(
                selectinload(Beneficiary.unit),
                selectinload(Beneficiary.referent),
                selectinload(Beneficiary.contacts),
                selectinload(Beneficiary.medical_data),
                selectinload(Beneficiary.pais),
            )
            .where(Beneficiary.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all_filtered(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
        unit_id: int | None = None,
        referent_id: int | None = None,
        search: str | None = None,
        sort: str | None = None,
    ) -> tuple[list[Beneficiary], int]:
        """Get all beneficiaries with filtering and pagination."""
        query = (
            select(Beneficiary)
            .options(
                selectinload(Beneficiary.unit),
                selectinload(Beneficiary.referent),
            )
        )

        # Apply filters
        if status:
            query = query.where(Beneficiary.status == status)
        if unit_id:
            query = query.where(Beneficiary.unit_id == unit_id)
        if referent_id:
            query = query.where(Beneficiary.referent_id == referent_id)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Beneficiary.first_name.ilike(search_pattern),
                    Beneficiary.last_name.ilike(search_pattern),
                )
            )

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Apply sorting
        if sort:
            if sort.startswith("-"):
                sort_field = sort[1:]
                desc = True
            else:
                sort_field = sort
                desc = False

            if hasattr(Beneficiary, sort_field):
                column = getattr(Beneficiary, sort_field)
                query = query.order_by(column.desc() if desc else column)
        else:
            query = query.order_by(Beneficiary.last_name, Beneficiary.first_name)

        # Paginated query
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        beneficiaries = list(result.scalars().all())

        return beneficiaries, total

    async def get_by_referent(self, referent_id: int) -> list[Beneficiary]:
        """Get beneficiaries by referent ID."""
        result = await self.db.execute(
            select(Beneficiary)
            .options(selectinload(Beneficiary.unit))
            .where(Beneficiary.referent_id == referent_id)
            .where(Beneficiary.status == "active")
            .order_by(Beneficiary.last_name, Beneficiary.first_name)
        )
        return list(result.scalars().all())

    async def get_by_unit(self, unit_id: int) -> list[Beneficiary]:
        """Get beneficiaries by unit ID."""
        result = await self.db.execute(
            select(Beneficiary)
            .where(Beneficiary.unit_id == unit_id)
            .where(Beneficiary.status == "active")
            .order_by(Beneficiary.last_name, Beneficiary.first_name)
        )
        return list(result.scalars().all())

    # Medical data operations
    async def get_medical_data(self, beneficiary_id: int) -> BeneficiaryMedicalData | None:
        """Get medical data for a beneficiary."""
        result = await self.db.execute(
            select(BeneficiaryMedicalData)
            .where(BeneficiaryMedicalData.beneficiary_id == beneficiary_id)
        )
        return result.scalar_one_or_none()

    async def create_or_update_medical_data(
        self,
        beneficiary_id: int,
        data: dict,
        updated_by: int,
    ) -> BeneficiaryMedicalData:
        """Create or update medical data for a beneficiary."""
        medical_data = await self.get_medical_data(beneficiary_id)

        if medical_data:
            for key, value in data.items():
                if hasattr(medical_data, key):
                    setattr(medical_data, key, value)
            medical_data.updated_by = updated_by
        else:
            medical_data = BeneficiaryMedicalData(
                beneficiary_id=beneficiary_id,
                updated_by=updated_by,
                **data,
            )
            self.db.add(medical_data)

        await self.db.flush()
        return medical_data

    # Contact operations
    async def get_contacts(self, beneficiary_id: int) -> list[Contact]:
        """Get contacts for a beneficiary."""
        result = await self.db.execute(
            select(Contact)
            .where(Contact.beneficiary_id == beneficiary_id)
            .order_by(Contact.is_emergency_contact.desc(), Contact.name)
        )
        return list(result.scalars().all())

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        """Get contact by ID."""
        result = await self.db.execute(
            select(Contact).where(Contact.id == contact_id)
        )
        return result.scalar_one_or_none()

    async def create_contact(self, beneficiary_id: int, data: dict) -> Contact:
        """Create a contact for a beneficiary."""
        contact = Contact(beneficiary_id=beneficiary_id, **data)
        self.db.add(contact)
        await self.db.flush()
        await self.db.refresh(contact)
        return contact

    async def update_contact(self, contact: Contact, data: dict) -> Contact:
        """Update a contact."""
        for key, value in data.items():
            if hasattr(contact, key) and value is not None:
                setattr(contact, key, value)
        await self.db.flush()
        await self.db.refresh(contact)
        return contact

    async def delete_contact(self, contact: Contact) -> None:
        """Delete a contact."""
        await self.db.delete(contact)
        await self.db.flush()

    # Risk behavior operations
    async def get_risk_behaviors(
        self,
        beneficiary_id: int,
        active_only: bool = True,
    ) -> list[RiskBehavior]:
        """Get risk behaviors for a beneficiary."""
        query = select(RiskBehavior).where(RiskBehavior.beneficiary_id == beneficiary_id)

        if active_only:
            query = query.where(RiskBehavior.is_active == True)

        query = query.order_by(RiskBehavior.reported_date.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_risk_behavior_by_id(self, risk_id: int) -> RiskBehavior | None:
        """Get risk behavior by ID."""
        result = await self.db.execute(
            select(RiskBehavior).where(RiskBehavior.id == risk_id)
        )
        return result.scalar_one_or_none()

    async def create_risk_behavior(
        self,
        beneficiary_id: int,
        data: dict,
        reported_by: int,
    ) -> RiskBehavior:
        """Create a risk behavior for a beneficiary."""
        risk = RiskBehavior(
            beneficiary_id=beneficiary_id,
            reported_by=reported_by,
            **data,
        )
        self.db.add(risk)
        await self.db.flush()
        await self.db.refresh(risk)
        return risk

    async def update_risk_behavior(self, risk: RiskBehavior, data: dict) -> RiskBehavior:
        """Update a risk behavior."""
        for key, value in data.items():
            if hasattr(risk, key) and value is not None:
                setattr(risk, key, value)
        await self.db.flush()
        await self.db.refresh(risk)
        return risk
