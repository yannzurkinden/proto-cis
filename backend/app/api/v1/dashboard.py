"""Dashboard endpoints."""

from datetime import date, datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_management
from app.models.beneficiary import Beneficiary
from app.models.objective import Objective
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

        # Get latest journal entry for this beneficiary
        latest_entries = await journal_repo.get_recent_entries(
            beneficiary_id=b.id, limit=1
        )
        last_entry_date = latest_entries[0].entry_date.date() if latest_entries else None

        my_beneficiaries.append(
            BeneficiarySummary(
                id=b.id,
                name=b.full_name,
                photo_url=b.photo_url,
                status=b.status,
                objectives_overdue=overdue_count,
                last_journal_entry=last_entry_date,
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
                beneficiary_name=obj.beneficiary.full_name if obj.beneficiary else "Inconnu",
                objective_id=obj.id,
                objective_title=obj.title,
                due_date=obj.due_date,
                message=f"Objectif en retard depuis le {obj.due_date}",
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
                beneficiary_name=obj.beneficiary.full_name if obj.beneficiary else "Inconnu",
                message=f"L'objectif '{obj.title}' est en retard",
            )
        )

    # Calculate monthly statistics
    first_of_month = date.today().replace(day=1)
    first_of_month_dt = datetime(
        first_of_month.year, first_of_month.month, first_of_month.day,
        tzinfo=timezone.utc,
    )

    # Count new beneficiaries this month (entry_date >= first of month)
    new_query = select(func.count()).select_from(Beneficiary).where(
        Beneficiary.entry_date >= first_of_month,
    )
    if unit_id:
        new_query = new_query.where(Beneficiary.unit_id == unit_id)
    new_this_month = (await db.execute(new_query)).scalar() or 0

    # Count exited beneficiaries this month (exit_date >= first of month)
    exited_query = select(func.count()).select_from(Beneficiary).where(
        Beneficiary.exit_date >= first_of_month,
    )
    if unit_id:
        exited_query = exited_query.where(Beneficiary.unit_id == unit_id)
    exited_this_month = (await db.execute(exited_query)).scalar() or 0

    # Count objectives achieved this month
    achieved_query = select(func.count()).select_from(Objective).where(
        Objective.status == "achieved",
        Objective.updated_at >= first_of_month_dt,
    )
    if unit_id:
        achieved_query = achieved_query.join(Beneficiary).where(
            Beneficiary.unit_id == unit_id
        )
    achieved_this_month = (await db.execute(achieved_query)).scalar() or 0

    return ManagementDashboardResponse(
        summary=BeneficiarySummaryStats(
            total_beneficiaries=total_beneficiaries,
            active_beneficiaries=active_beneficiaries,
            new_this_month=new_this_month,
            exited_this_month=exited_this_month,
        ),
        objectives_overview=ObjectivesOverviewSummary(
            total=stats["total"],
            achieved_this_month=achieved_this_month,
            overdue=stats["overdue"],
            achievement_rate=achievement_rate,
        ),
        absence_stats=AbsenceStatsSummary(
            global_rate=0.0,  # Absence rate requires time tracking data integration
            by_unit=[],
        ),
        alerts=alerts,
    )
