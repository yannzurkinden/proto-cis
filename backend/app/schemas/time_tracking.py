"""Time tracking schemas."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


# Time Entries
class TimeEntryBase(BaseModel):
    """Base time entry schema."""

    entry_date: date
    time_in: time | None = None
    time_out: time | None = None
    entry_type: Literal["work", "training", "appointment"] = "work"
    notes: str | None = None


class TimeEntryCreate(TimeEntryBase):
    """Schema for creating a time entry."""

    pass


class TimeEntryUpdate(BaseModel):
    """Schema for updating a time entry."""

    time_in: time | None = None
    time_out: time | None = None
    entry_type: Literal["work", "training", "appointment"] | None = None
    notes: str | None = None


class TimeEntryResponse(TimeEntryBase):
    """Schema for time entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: int
    hours_worked: Decimal | None = None


# Absences
class AbsenceBase(BaseModel):
    """Base absence schema."""

    absence_type: Literal["sick", "vacation", "accident", "unauthorized", "other"]
    start_date: date
    end_date: date
    notes: str | None = None


class AbsenceCreate(AbsenceBase):
    """Schema for creating an absence."""

    pass


class AbsenceUpdate(BaseModel):
    """Schema for updating an absence."""

    absence_type: Literal["sick", "vacation", "accident", "unauthorized", "other"] | None = None
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class AbsenceResponse(AbsenceBase):
    """Schema for absence response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: int
    justification_document_id: int | None = None
    validated_by: int | None = None
    validated_at: datetime | None = None
    duration_days: int


# Vacation Balance
class VacationBalanceResponse(BaseModel):
    """Schema for vacation balance response."""

    model_config = ConfigDict(from_attributes=True)

    year: int
    entitled_days: Decimal
    taken_days: Decimal
    remaining_days: Decimal
    pending_requests: Decimal = Decimal("0")


# Absence Statistics
class MonthlyAbsence(BaseModel):
    """Monthly absence breakdown."""

    month: str
    days: int


class AbsenceStatsResponse(BaseModel):
    """Schema for absence statistics response."""

    total_days: int
    by_type: dict
    absence_rate: float
    monthly_breakdown: list[MonthlyAbsence] = []
