"""PAI (Plan d'Accompagnement Individualis) endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_msp_or_above
from app.models.user import User
from app.repositories.beneficiary_repository import BeneficiaryRepository
from app.repositories.pai_repository import PAIRepository
from app.schemas.pai import ObjectiveSummary, PAICreate, PAIResponse, PAIUpdate

router = APIRouter()


@router.get("/{pai_id}", response_model=PAIResponse)
async def get_pai(
    pai_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a specific PAI by ID."""
    pai_repo = PAIRepository(db)
    pai = await pai_repo.get_by_id_with_objectives(pai_id)

    if not pai:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PAI not found",
        )

    # Build objectives summary
    objectives = []
    for obj in pai.objectives:
        objectives.append(
            ObjectiveSummary(
                id=obj.id,
                title=obj.title,
                objective_type=obj.objective_type,
                term=obj.term,
                status=obj.status,
                progress=obj.progress,
                due_date=obj.due_date,
            )
        )

    return PAIResponse(
        id=pai.id,
        beneficiary_id=pai.beneficiary_id,
        status=pai.status,
        valid_from=pai.valid_from,
        valid_to=pai.valid_to,
        strengths=pai.strengths,
        difficulties=pai.difficulties,
        beneficiary_wishes=pai.beneficiary_wishes,
        objectives=objectives,
        created_at=pai.created_at,
        created_by=pai.created_by,
    )


@router.put("/{pai_id}", response_model=PAIResponse)
async def update_pai(
    pai_id: int,
    pai_data: PAIUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update a PAI."""
    pai_repo = PAIRepository(db)
    pai = await pai_repo.get_by_id(pai_id)

    if not pai:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PAI not found",
        )

    update_data = pai_data.model_dump(exclude_unset=True)
    pai = await pai_repo.update(pai, update_data)
    pai = await pai_repo.get_by_id_with_objectives(pai.id)

    objectives = []
    for obj in pai.objectives:
        objectives.append(
            ObjectiveSummary(
                id=obj.id,
                title=obj.title,
                objective_type=obj.objective_type,
                term=obj.term,
                status=obj.status,
                progress=obj.progress,
                due_date=obj.due_date,
            )
        )

    return PAIResponse(
        id=pai.id,
        beneficiary_id=pai.beneficiary_id,
        status=pai.status,
        valid_from=pai.valid_from,
        valid_to=pai.valid_to,
        strengths=pai.strengths,
        difficulties=pai.difficulties,
        beneficiary_wishes=pai.beneficiary_wishes,
        objectives=objectives,
        created_at=pai.created_at,
        created_by=pai.created_by,
    )


@router.post("/{pai_id}/activate", response_model=PAIResponse)
async def activate_pai(
    pai_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Activate a PAI (deactivates other active PAIs for the same beneficiary)."""
    pai_repo = PAIRepository(db)
    pai = await pai_repo.get_by_id(pai_id)

    if not pai:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PAI not found",
        )

    pai = await pai_repo.activate_pai(pai)
    pai = await pai_repo.get_by_id_with_objectives(pai.id)

    objectives = []
    for obj in pai.objectives:
        objectives.append(
            ObjectiveSummary(
                id=obj.id,
                title=obj.title,
                objective_type=obj.objective_type,
                term=obj.term,
                status=obj.status,
                progress=obj.progress,
                due_date=obj.due_date,
            )
        )

    return PAIResponse(
        id=pai.id,
        beneficiary_id=pai.beneficiary_id,
        status=pai.status,
        valid_from=pai.valid_from,
        valid_to=pai.valid_to,
        strengths=pai.strengths,
        difficulties=pai.difficulties,
        beneficiary_wishes=pai.beneficiary_wishes,
        objectives=objectives,
        created_at=pai.created_at,
        created_by=pai.created_by,
    )


@router.post("/{pai_id}/close", response_model=PAIResponse)
async def close_pai(
    pai_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Close a PAI."""
    pai_repo = PAIRepository(db)
    pai = await pai_repo.get_by_id(pai_id)

    if not pai:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PAI not found",
        )

    pai = await pai_repo.close_pai(pai)
    pai = await pai_repo.get_by_id_with_objectives(pai.id)

    objectives = []
    for obj in pai.objectives:
        objectives.append(
            ObjectiveSummary(
                id=obj.id,
                title=obj.title,
                objective_type=obj.objective_type,
                term=obj.term,
                status=obj.status,
                progress=obj.progress,
                due_date=obj.due_date,
            )
        )

    return PAIResponse(
        id=pai.id,
        beneficiary_id=pai.beneficiary_id,
        status=pai.status,
        valid_from=pai.valid_from,
        valid_to=pai.valid_to,
        strengths=pai.strengths,
        difficulties=pai.difficulties,
        beneficiary_wishes=pai.beneficiary_wishes,
        objectives=objectives,
        created_at=pai.created_at,
        created_by=pai.created_by,
    )


# Beneficiary PAI endpoints (nested under beneficiaries)
from fastapi import APIRouter as NestedRouter  # noqa: E402

beneficiary_pais_router = NestedRouter()


@beneficiary_pais_router.get("/{beneficiary_id}/pais", response_model=list[PAIResponse])
async def list_beneficiary_pais(
    beneficiary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    pai_status: str | None = Query(None, alias="status"),
):
    """List all PAIs for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    pai_repo = PAIRepository(db)
    pais = await pai_repo.get_by_beneficiary(beneficiary_id, status=pai_status)

    result = []
    for pai in pais:
        objectives = []
        for obj in pai.objectives:
            objectives.append(
                ObjectiveSummary(
                    id=obj.id,
                    title=obj.title,
                    objective_type=obj.objective_type,
                    term=obj.term,
                    status=obj.status,
                    progress=obj.progress,
                    due_date=obj.due_date,
                )
            )

        result.append(
            PAIResponse(
                id=pai.id,
                beneficiary_id=pai.beneficiary_id,
                status=pai.status,
                valid_from=pai.valid_from,
                valid_to=pai.valid_to,
                strengths=pai.strengths,
                difficulties=pai.difficulties,
                beneficiary_wishes=pai.beneficiary_wishes,
                objectives=objectives,
                created_at=pai.created_at,
                created_by=pai.created_by,
            )
        )

    return result


@beneficiary_pais_router.post(
    "/{beneficiary_id}/pais",
    response_model=PAIResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_beneficiary_pai(
    beneficiary_id: int,
    pai_data: PAICreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Create a new PAI for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    pai_repo = PAIRepository(db)
    pai = await pai_repo.create_pai(
        beneficiary_id=beneficiary_id,
        data=pai_data.model_dump(),
        created_by=current_user.id,
    )

    return PAIResponse(
        id=pai.id,
        beneficiary_id=pai.beneficiary_id,
        status=pai.status,
        valid_from=pai.valid_from,
        valid_to=pai.valid_to,
        strengths=pai.strengths,
        difficulties=pai.difficulties,
        beneficiary_wishes=pai.beneficiary_wishes,
        objectives=[],
        created_at=pai.created_at,
        created_by=pai.created_by,
    )
