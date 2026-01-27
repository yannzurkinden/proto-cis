"""Time tracking schemas."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# Time Entries
class TimeEntryBase(BaseModel):
    """Base time entry schema."""

    entry_date: date
    time_in: Optional[time] = None
    time_out: Optional[time] = None
    entry_type: Literal["work", "training", "appointment"] = "work"
    notes: Optional[str] = None


class TimeEntryCreate(TimeEntryBase):
    """Schema for creating a time entry."""

    pass


class TimeEntryUpdate(BaseModel):
    """Schema for updating a time entry."""

    time_in: Optional[time] = None
    time_out: Optional[time] = None
    entry_type: Optional[Literal["work", "training", "appointment"]] = None
    notes: Optional[str] = None


class TimeEntryResponse(TimeEntryBase):
    """Schema for time entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: int
    hours_worked: Optional[Decimal] = None


# Absences
class AbsenceBase(BaseModel):
    """Base absence schema."""

    absence_type: Literal["sick", "vacation", "accident", "unauthorized", "other"]
    start_date: date
    end_date: date
    notes: Optional[str] = None


class AbsenceCreate(AbsenceBase):
    """Schema for creating an absence."""

    pass


class AbsenceUpdate(BaseModel):
    """Schema for updating an absence."""

    absence_type: Optional[Literal["sick", "vacation", "accident", "unauthorized", "other"]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class AbsenceResponse(AbsenceBase):
    """Schema for absence response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: int
    justification_document_id: Optional[int] = None
    validated_by: Optional[int] = None
    validated_at: Optional[datetime] = None
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
    monthly_breakdown: List[MonthlyAbsence]
