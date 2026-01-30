"""Time tracking repository for database operations."""

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.time_tracking import Absence, TimeEntry, VacationBalance
from app.repositories.base import BaseRepository


class TimeTrackingRepository(BaseRepository[TimeEntry]):
    """Repository for TimeEntry model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, TimeEntry)

    # Time entry operations

    async def get_time_entries(
        self,
        beneficiary_id: int,
        date_from: date | None = None,
        date_to: date | None = None,
        entry_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[TimeEntry], int]:
        """Get time entries for a beneficiary with filtering and pagination."""
        query = select(TimeEntry).where(TimeEntry.beneficiary_id == beneficiary_id)

        if date_from:
            query = query.where(TimeEntry.entry_date >= date_from)
        if date_to:
            query = query.where(TimeEntry.entry_date <= date_to)
        if entry_type:
            query = query.where(TimeEntry.entry_type == entry_type)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginated query
        query = query.offset(skip).limit(limit).order_by(TimeEntry.entry_date.desc())
        result = await self.db.execute(query)
        entries = list(result.scalars().all())

        return entries, total

    async def get_time_entry_by_id(self, entry_id: int) -> TimeEntry | None:
        """Get a time entry by ID."""
        result = await self.db.execute(
            select(TimeEntry).where(TimeEntry.id == entry_id)
        )
        return result.scalar_one_or_none()

    async def create_time_entry(self, beneficiary_id: int, data: dict) -> TimeEntry:
        """Create a time entry for a beneficiary with auto-calculated hours."""
        entry = TimeEntry(beneficiary_id=beneficiary_id, **data)

        # Auto-calculate hours_worked if time_in and time_out are provided
        if entry.hours_worked is None:
            calculated = entry.calculate_hours()
            if calculated is not None:
                entry.hours_worked = calculated

        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def update_time_entry(self, entry: TimeEntry, data: dict) -> TimeEntry:
        """Update a time entry."""
        for key, value in data.items():
            if hasattr(entry, key) and value is not None:
                setattr(entry, key, value)

        # Recalculate hours_worked if time fields changed
        if "time_in" in data or "time_out" in data:
            calculated = entry.calculate_hours()
            if calculated is not None:
                entry.hours_worked = calculated

        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def delete_time_entry(self, entry: TimeEntry) -> None:
        """Delete a time entry."""
        await self.db.delete(entry)
        await self.db.flush()

    # Absence operations

    async def get_absences(
        self,
        beneficiary_id: int,
        absence_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Absence], int]:
        """Get absences for a beneficiary with filtering and pagination."""
        query = select(Absence).where(Absence.beneficiary_id == beneficiary_id)

        if absence_type:
            query = query.where(Absence.absence_type == absence_type)
        if date_from:
            query = query.where(Absence.start_date >= date_from)
        if date_to:
            query = query.where(Absence.end_date <= date_to)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginated query
        query = query.offset(skip).limit(limit).order_by(Absence.start_date.desc())
        result = await self.db.execute(query)
        absences = list(result.scalars().all())

        return absences, total

    async def get_absence_by_id(self, absence_id: int) -> Absence | None:
        """Get an absence by ID."""
        result = await self.db.execute(
            select(Absence).where(Absence.id == absence_id)
        )
        return result.scalar_one_or_none()

    async def create_absence(self, beneficiary_id: int, data: dict) -> Absence:
        """Create an absence for a beneficiary."""
        absence = Absence(beneficiary_id=beneficiary_id, **data)
        self.db.add(absence)
        await self.db.flush()
        await self.db.refresh(absence)
        return absence

    async def update_absence(self, absence: Absence, data: dict) -> Absence:
        """Update an absence."""
        for key, value in data.items():
            if hasattr(absence, key) and value is not None:
                setattr(absence, key, value)
        await self.db.flush()
        await self.db.refresh(absence)
        return absence

    async def delete_absence(self, absence: Absence) -> None:
        """Delete an absence."""
        await self.db.delete(absence)
        await self.db.flush()

    async def validate_absence(self, absence: Absence, validated_by: int) -> Absence:
        """Validate an absence."""
        absence.validated_by = validated_by
        absence.validated_at = datetime.now(UTC)
        await self.db.flush()
        await self.db.refresh(absence)
        return absence

    # Vacation balance operations

    async def get_vacation_balance(
        self,
        beneficiary_id: int,
        year: int,
    ) -> VacationBalance | None:
        """Get vacation balance for a beneficiary and year."""
        result = await self.db.execute(
            select(VacationBalance)
            .where(VacationBalance.beneficiary_id == beneficiary_id)
            .where(VacationBalance.year == year)
        )
        return result.scalar_one_or_none()

    async def get_or_create_vacation_balance(
        self,
        beneficiary_id: int,
        year: int,
        entitled_days: Decimal = Decimal("25"),
    ) -> VacationBalance:
        """Get or create vacation balance for a beneficiary and year."""
        balance = await self.get_vacation_balance(beneficiary_id, year)

        if balance:
            return balance

        balance = VacationBalance(
            beneficiary_id=beneficiary_id,
            year=year,
            entitled_days=entitled_days,
            taken_days=Decimal("0"),
        )
        self.db.add(balance)
        await self.db.flush()
        await self.db.refresh(balance)
        return balance

    # Statistics

    async def get_absence_stats(
        self,
        beneficiary_id: int,
        year: int | None = None,
    ) -> dict:
        """Get absence statistics for a beneficiary."""
        query = select(Absence).where(Absence.beneficiary_id == beneficiary_id)

        if year:
            query = query.where(extract("year", Absence.start_date) == year)

        result = await self.db.execute(query)
        absences = list(result.scalars().all())

        total_days = sum(a.duration_days for a in absences)

        by_type: dict[str, int] = {}
        for absence in absences:
            by_type[absence.absence_type] = by_type.get(absence.absence_type, 0) + absence.duration_days

        # Calculate absence rate (working days in a year ~ 252)
        working_days = 252
        absence_rate = round((total_days / working_days) * 100, 2) if working_days > 0 else 0

        return {
            "total_days": total_days,
            "by_type": by_type,
            "absence_rate": absence_rate,
        }

    async def get_monthly_hours(
        self,
        beneficiary_id: int,
        year: int,
        month: int,
    ) -> Decimal:
        """Get total hours worked in a given month."""
        result = await self.db.execute(
            select(func.coalesce(func.sum(TimeEntry.hours_worked), 0))
            .where(TimeEntry.beneficiary_id == beneficiary_id)
            .where(extract("year", TimeEntry.entry_date) == year)
            .where(extract("month", TimeEntry.entry_date) == month)
        )
        return Decimal(str(result.scalar() or 0))
