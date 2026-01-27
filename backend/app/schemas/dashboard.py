"""Dashboard schemas."""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class BeneficiarySummary(BaseModel):
    """Summary of a beneficiary for dashboard."""

    id: int
    name: str
    photo_url: Optional[str] = None
    status: str
    objectives_overdue: int = 0
    last_journal_entry: Optional[date] = None


class ReminderItem(BaseModel):
    """Reminder item for dashboard."""

    type: str
    beneficiary_id: int
    beneficiary_name: str
    objective_id: Optional[int] = None
    objective_title: Optional[str] = None
    due_date: Optional[date] = None
    message: Optional[str] = None


class MSPDashboardResponse(BaseModel):
    """Schema for MSP dashboard response."""

    my_beneficiaries: List[BeneficiarySummary]
    today_reminders: List[ReminderItem]
    recent_journal_entries: List[dict]
    pending_tasks: List[dict]


class UnitStats(BaseModel):
    """Statistics for a unit."""

    unit_id: int
    unit_name: str
    rate: float


class ObjectivesOverviewSummary(BaseModel):
    """Summary of objectives."""

    total: int
    achieved_this_month: int
    overdue: int
    achievement_rate: float


class AbsenceStatsSummary(BaseModel):
    """Summary of absence statistics."""

    global_rate: float
    by_unit: List[UnitStats]


class BeneficiarySummaryStats(BaseModel):
    """Summary of beneficiary statistics."""

    total_beneficiaries: int
    active_beneficiaries: int
    new_this_month: int
    exited_this_month: int


class Alert(BaseModel):
    """Alert for dashboard."""

    type: str
    beneficiary_id: int
    beneficiary_name: str
    message: str


class ManagementDashboardResponse(BaseModel):
    """Schema for management dashboard response."""

    summary: BeneficiarySummaryStats
    objectives_overview: ObjectivesOverviewSummary
    absence_stats: AbsenceStatsSummary
    alerts: List[Alert]
