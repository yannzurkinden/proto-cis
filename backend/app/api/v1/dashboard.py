"""Dashboard endpoints."""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_management
from app.models.user import User
from app.repositories.beneficiary_repository import BeneficiaryRepository
from app.repositories.objective_repository import ObjectiveRepository
from app.repositories.journal_repository import JournalRepository
from app.schemas.dashboard import (
    MSPDashboardResponse,
    ManagementDashboardResponse,
    BeneficiarySummary,
    ReminderItem,
    BeneficiarySummaryStats,
    ObjectivesOverviewSummary,
    AbsenceStatsSummary,
    UnitStats,
    Alert,
)

router = APIRouter()


@router.get("/msp", response_model=MSPDashboardResponse)
async def get_msp_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get MSP dashboard data."""
    beneficiary_repo = BeneficiaryRepository(db)
    objective_repo = ObjectiveRepository(db)
    journal_repo = JournalRepository(db)

    # Get beneficiaries for this MSP
    beneficiaries = await beneficiary_repo.get_by_referent(current_user.id)

    my_beneficiaries = []
    for b in beneficiaries:
        # Get overdue objectives count
        overdue_objectives = await objective_repo.get_overdue_objectives(
            referent_id=current_user.id
        )
        overdue_count = sum(1 for o in overdue_objectives if o.beneficiary_id == b.id)

        my_beneficiaries.append(
            BeneficiarySummary(
                id=b.id,
                name=b.full_name,
                photo_url=b.photo_url,
                status=b.status,
                objectives_overdue=overdue_count,
                last_journal_entry=None,  # TODO: Calculate
            )
        )

    # Get reminders (overdue objectives)
    overdue_objectives = await objective_repo.get_overdue_objectives(
        referent_id=current_user.id
    )

    today_reminders = []
    for obj in overdue_objectives[:10]:  # Limit to 10
        today_reminders.append(
            ReminderItem(
                type="objective_overdue",
                beneficiary_id=obj.beneficiary_id,
                beneficiary_name=obj.beneficiary.full_name if obj.beneficiary else "Unknown",
                objective_id=obj.id,
                objective_title=obj.title,
                due_date=obj.due_date,
                message=f"Objective overdue since {obj.due_date}",
            )
        )

    # Get recent journal entries
    recent_entries = await journal_repo.get_recent_entries(
        unit_id=current_user.unit_id,
        limit=10,
    )

    recent_journal = []
    for entry in recent_entries:
        recent_journal.append({
            "id": entry.id,
            "beneficiary_name": entry.beneficiary.full_name if entry.beneficiary else "Unknown",
            "title": entry.title,
            "entry_date": entry.entry_date.isoformat(),
        })

    return MSPDashboardResponse(
        my_beneficiaries=my_beneficiaries,
        today_reminders=today_reminders,
        recent_journal_entries=recent_journal,
        pending_tasks=[],
    )


@router.get("/management", response_model=ManagementDashboardResponse)
async def get_management_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
    unit_id: Optional[int] = None,
):
    """Get management dashboard data."""
    beneficiary_repo = BeneficiaryRepository(db)
    objective_repo = ObjectiveRepository(db)

    # Use user's unit if not specified and user is RES
    if unit_id is None and current_user.role == "RES":
        unit_id = current_user.unit_id

    # Get beneficiary statistics
    if unit_id:
        beneficiaries = await beneficiary_repo.get_by_unit(unit_id)
    else:
        beneficiaries, _ = await beneficiary_repo.get_all_filtered(
            skip=0, limit=1000, status="active"
        )

    total_beneficiaries = len(beneficiaries)
    active_beneficiaries = sum(1 for b in beneficiaries if b.status == "active")

    # Get objectives statistics
    stats = await objective_repo.get_objectives_stats(unit_id=unit_id)

    achievement_rate = 0.0
    if stats["total"] > 0:
        achievement_rate = (stats["achieved"] / stats["total"]) * 100

    # Get overdue objectives for alerts
    overdue_objectives = await objective_repo.get_overdue_objectives(unit_id=unit_id)

    alerts = []
    for obj in overdue_objectives[:5]:
        alerts.append(
            Alert(
                type="objective_overdue",
                beneficiary_id=obj.beneficiary_id,
                beneficiary_name=obj.beneficiary.full_name if obj.beneficiary else "Unknown",
                message=f"Objective '{obj.title}' is overdue",
            )
        )

    return ManagementDashboardResponse(
        summary=BeneficiarySummaryStats(
            total_beneficiaries=total_beneficiaries,
            active_beneficiaries=active_beneficiaries,
            new_this_month=0,  # TODO: Calculate
            exited_this_month=0,  # TODO: Calculate
        ),
        objectives_overview=ObjectivesOverviewSummary(
            total=stats["total"],
            achieved_this_month=0,  # TODO: Calculate
            overdue=stats["overdue"],
            achievement_rate=achievement_rate,
        ),
        absence_stats=AbsenceStatsSummary(
            global_rate=0.0,  # TODO: Calculate
            by_unit=[],
        ),
        alerts=alerts,
    )
