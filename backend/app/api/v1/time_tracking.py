"""Time tracking endpoints for time entries, absences, and vacation balance."""

from datetime import date, datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_management, require_msp_or_above
from app.models.user import User
from app.repositories.beneficiary_repository import BeneficiaryRepository
from app.repositories.time_tracking_repository import TimeTrackingRepository
from app.schemas.time_tracking import (
    AbsenceCreate,
    AbsenceResponse,
    AbsenceStatsResponse,
    AbsenceUpdate,
    TimeEntryCreate,
    TimeEntryResponse,
    TimeEntryUpdate,
    VacationBalanceResponse,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


# --- Time Entries ---


@router.get(
    "/{beneficiary_id}/time-entries",
    response_model=PaginatedResponse[TimeEntryResponse],
)
async def list_time_entries(
    beneficiary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    """List time entries for a beneficiary, filterable by date range."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    time_repo = TimeTrackingRepository(db)
    skip = (page - 1) * size

    entries, total = await time_repo.get_time_entries(
        beneficiary_id=beneficiary_id,
        skip=skip,
        limit=size,
        date_from=date_from,
        date_to=date_to,
    )

    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedResponse(
        items=[TimeEntryResponse.model_validate(e) for e in entries],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post(
    "/{beneficiary_id}/time-entries",
    response_model=TimeEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_time_entry(
    beneficiary_id: int,
    entry_data: TimeEntryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Create a time entry for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    time_repo = TimeTrackingRepository(db)
    entry = await time_repo.create_time_entry(
        beneficiary_id=beneficiary_id,
        data=entry_data.model_dump(),
    )
    return TimeEntryResponse.model_validate(entry)


@router.put(
    "/{beneficiary_id}/time-entries/{entry_id}",
    response_model=TimeEntryResponse,
)
async def update_time_entry(
    beneficiary_id: int,
    entry_id: int,
    entry_data: TimeEntryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update a time entry."""
    time_repo = TimeTrackingRepository(db)
    entry = await time_repo.get_time_entry_by_id(entry_id)

    if not entry or entry.beneficiary_id != beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found",
        )

    update_data = entry_data.model_dump(exclude_unset=True)
    entry = await time_repo.update_time_entry(entry, update_data)
    return TimeEntryResponse.model_validate(entry)


@router.delete(
    "/{beneficiary_id}/time-entries/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_time_entry(
    beneficiary_id: int,
    entry_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Delete a time entry."""
    time_repo = TimeTrackingRepository(db)
    entry = await time_repo.get_time_entry_by_id(entry_id)

    if not entry or entry.beneficiary_id != beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found",
        )

    await time_repo.delete_time_entry(entry)


# --- Absences ---


@router.get(
    "/{beneficiary_id}/absences",
    response_model=PaginatedResponse[AbsenceResponse],
)
async def list_absences(
    beneficiary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    absence_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    """List absences for a beneficiary, filterable by type and date range."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    time_repo = TimeTrackingRepository(db)
    skip = (page - 1) * size

    absences, total = await time_repo.get_absences(
        beneficiary_id=beneficiary_id,
        skip=skip,
        limit=size,
        absence_type=absence_type,
        date_from=date_from,
        date_to=date_to,
    )

    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedResponse(
        items=[AbsenceResponse.model_validate(a) for a in absences],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post(
    "/{beneficiary_id}/absences",
    response_model=AbsenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_absence(
    beneficiary_id: int,
    absence_data: AbsenceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Create an absence record for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    time_repo = TimeTrackingRepository(db)
    absence = await time_repo.create_absence(
        beneficiary_id=beneficiary_id,
        data=absence_data.model_dump(),
    )
    return AbsenceResponse.model_validate(absence)


@router.put(
    "/{beneficiary_id}/absences/{absence_id}",
    response_model=AbsenceResponse,
)
async def update_absence(
    beneficiary_id: int,
    absence_id: int,
    absence_data: AbsenceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update an absence record."""
    time_repo = TimeTrackingRepository(db)
    absence = await time_repo.get_absence_by_id(absence_id)

    if not absence or absence.beneficiary_id != beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence not found",
        )

    update_data = absence_data.model_dump(exclude_unset=True)
    absence = await time_repo.update_absence(absence, update_data)
    return AbsenceResponse.model_validate(absence)


@router.delete(
    "/{beneficiary_id}/absences/{absence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_absence(
    beneficiary_id: int,
    absence_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Delete an absence record."""
    time_repo = TimeTrackingRepository(db)
    absence = await time_repo.get_absence_by_id(absence_id)

    if not absence or absence.beneficiary_id != beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence not found",
        )

    await time_repo.delete_absence(absence)


@router.post(
    "/{beneficiary_id}/absences/{absence_id}/validate",
    response_model=AbsenceResponse,
)
async def validate_absence(
    beneficiary_id: int,
    absence_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
):
    """Validate an absence (management only)."""
    time_repo = TimeTrackingRepository(db)
    absence = await time_repo.get_absence_by_id(absence_id)

    if not absence or absence.beneficiary_id != beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Absence not found",
        )

    absence = await time_repo.validate_absence(
        absence=absence,
        validated_by=current_user.id,
    )
    return AbsenceResponse.model_validate(absence)


# --- Vacation Balance ---


@router.get(
    "/{beneficiary_id}/vacation-balance",
    response_model=VacationBalanceResponse,
)
async def get_vacation_balance(
    beneficiary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    year: Optional[int] = None,
):
    """Get vacation balance for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    time_repo = TimeTrackingRepository(db)
    current_year = year or date.today().year

    balance = await time_repo.get_vacation_balance(
        beneficiary_id=beneficiary_id,
        year=current_year,
    )

    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacation balance not found for the specified year",
        )

    return VacationBalanceResponse.model_validate(balance)


# --- Absence Statistics ---


@router.get(
    "/{beneficiary_id}/absence-stats",
    response_model=AbsenceStatsResponse,
)
async def get_absence_stats(
    beneficiary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    year: Optional[int] = None,
):
    """Get absence statistics for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    time_repo = TimeTrackingRepository(db)
    current_year = year or date.today().year

    stats = await time_repo.get_absence_stats(
        beneficiary_id=beneficiary_id,
        year=current_year,
    )

    return stats
