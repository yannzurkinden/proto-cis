"""Dashboard schemas."""

from datetime import date

from pydantic import BaseModel


class BeneficiarySummary(BaseModel):
    """Summary of a beneficiary for dashboard."""

    id: int
    name: str
    photo_url: str | None = None
    status: str
    objectives_overdue: int = 0
    last_journal_entry: date | None = None


class ReminderItem(BaseModel):
    """Reminder item for dashboard."""

    type: str
    beneficiary_id: int
    beneficiary_name: str
    objective_id: int | None = None
    objective_title: str | None = None
    due_date: date | None = None
    message: str | None = None


class MSPDashboardResponse(BaseModel):
    """Schema for MSP dashboard response."""

    my_beneficiaries: list[BeneficiarySummary]
    today_reminders: list[ReminderItem]
    recent_journal_entries: list[dict]
    pending_tasks: list[dict]


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
    by_unit: list[UnitStats]


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
    alerts: list[Alert]
