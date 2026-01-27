"""Objective management endpoints."""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_msp_or_above
from app.models.user import User
from app.repositories.objective_repository import ObjectiveRepository
from app.repositories.beneficiary_repository import BeneficiaryRepository
from app.schemas.objective import (
    ObjectiveCreate,
    ObjectiveUpdate,
    ObjectiveResponse,
    ObjectiveProgressUpdate,
    ObjectiveStatusUpdate,
    ActionCreate,
    ActionUpdate,
    ActionResponse,
    IndicatorResponse,
    ObjectivesOverviewResponse,
    ObjectiveOverview,
    BeneficiaryObjectives,
)
from app.schemas.common import PaginatedResponse, Message

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ObjectiveResponse])
async def list_objectives(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    beneficiary_id: Optional[int] = None,
    pai_id: Optional[int] = None,
    status: Optional[str] = None,
    objective_type: Optional[str] = None,
    term: Optional[str] = None,
    overdue: Optional[bool] = None,
):
    """List all objectives with filtering and pagination."""
    objective_repo = ObjectiveRepository(db)
    skip = (page - 1) * size

    # Apply unit filter based on user role
    unit_id = None
    if current_user.role == "MSP":
        # MSPs see objectives for their beneficiaries only
        pass  # Filter handled elsewhere
    elif current_user.role in ["RES"] and current_user.unit_id:
        unit_id = current_user.unit_id

    objectives, total = await objective_repo.get_all_filtered(
        skip=skip,
        limit=size,
        beneficiary_id=beneficiary_id,
        pai_id=pai_id,
        status=status,
        objective_type=objective_type,
        term=term,
        overdue=overdue,
        unit_id=unit_id,
    )

    items = []
    for obj in objectives:
        indicators = [IndicatorResponse.model_validate(i) for i in obj.indicators]
        actions = [ActionResponse.model_validate(a) for a in obj.actions]

        items.append(
            ObjectiveResponse(
                id=obj.id,
                pai_id=obj.pai_id,
                beneficiary_id=obj.beneficiary_id,
                beneficiary_name=obj.beneficiary.full_name if obj.beneficiary else None,
                title=obj.title,
                description=obj.description,
                objective_type=obj.objective_type,
                term=obj.term,
                priority=obj.priority,
                status=obj.status,
                progress=obj.progress,
                due_date=obj.due_date,
                reminder_frequency=obj.reminder_frequency,
                last_reminder_sent=obj.last_reminder_sent,
                indicators=indicators,
                actions=actions,
                created_at=obj.created_at,
            )
        )

    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/overview", response_model=ObjectivesOverviewResponse)
async def get_objectives_overview(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    unit_id: Optional[int] = None,
):
    """Get overview of all objectives with summary statistics."""
    objective_repo = ObjectiveRepository(db)

    # Get statistics
    stats = await objective_repo.get_objectives_stats(unit_id=unit_id)

    # Get objectives grouped by beneficiary
    objectives, _ = await objective_repo.get_all_filtered(
        skip=0,
        limit=1000,
        unit_id=unit_id,
    )

    # Group by beneficiary
    by_beneficiary_dict: dict = {}
    for obj in objectives:
        if obj.beneficiary_id not in by_beneficiary_dict:
            by_beneficiary_dict[obj.beneficiary_id] = {
                "beneficiary_id": obj.beneficiary_id,
                "beneficiary_name": obj.beneficiary.full_name if obj.beneficiary else "Unknown",
                "unit_name": obj.beneficiary.unit.name if obj.beneficiary and obj.beneficiary.unit else None,
                "objectives": [],
            }

        is_overdue = (
            obj.due_date is not None
            and obj.due_date < date.today()
            and obj.status in ["pending", "in_progress"]
        )

        by_beneficiary_dict[obj.beneficiary_id]["objectives"].append(
            ObjectiveOverview(
                id=obj.id,
                title=obj.title,
                status=obj.status,
                progress=obj.progress,
                due_date=obj.due_date,
                is_overdue=is_overdue,
            )
        )

    by_beneficiary = [
        BeneficiaryObjectives(**data) for data in by_beneficiary_dict.values()
    ]

    return ObjectivesOverviewResponse(
        summary=stats,
        by_beneficiary=by_beneficiary,
    )


@router.get("/{objective_id}", response_model=ObjectiveResponse)
async def get_objective(
    objective_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a specific objective by ID."""
    objective_repo = ObjectiveRepository(db)
    obj = await objective_repo.get_by_id_with_relations(objective_id)

    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objective not found",
        )

    indicators = [IndicatorResponse.model_validate(i) for i in obj.indicators]
    actions = [ActionResponse.model_validate(a) for a in obj.actions]

    return ObjectiveResponse(
        id=obj.id,
        pai_id=obj.pai_id,
        beneficiary_id=obj.beneficiary_id,
        beneficiary_name=obj.beneficiary.full_name if obj.beneficiary else None,
        title=obj.title,
        description=obj.description,
        objective_type=obj.objective_type,
        term=obj.term,
        priority=obj.priority,
        status=obj.status,
        progress=obj.progress,
        due_date=obj.due_date,
        reminder_frequency=obj.reminder_frequency,
        last_reminder_sent=obj.last_reminder_sent,
        indicators=indicators,
        actions=actions,
        created_at=obj.created_at,
    )


@router.post("", response_model=ObjectiveResponse, status_code=status.HTTP_201_CREATED)
async def create_objective(
    objective_data: ObjectiveCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Create a new objective."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(objective_data.beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    objective_repo = ObjectiveRepository(db)

    # Prepare data
    data = objective_data.model_dump(exclude={"indicators", "actions"})
    indicators = [i.model_dump() for i in (objective_data.indicators or [])]
    actions = [a.model_dump() for a in (objective_data.actions or [])]

    obj = await objective_repo.create_objective(
        data=data,
        indicators=indicators,
        actions=actions,
        created_by=current_user.id,
    )

    obj = await objective_repo.get_by_id_with_relations(obj.id)

    indicator_responses = [IndicatorResponse.model_validate(i) for i in obj.indicators]
    action_responses = [ActionResponse.model_validate(a) for a in obj.actions]

    return ObjectiveResponse(
        id=obj.id,
        pai_id=obj.pai_id,
        beneficiary_id=obj.beneficiary_id,
        title=obj.title,
        description=obj.description,
        objective_type=obj.objective_type,
        term=obj.term,
        priority=obj.priority,
        status=obj.status,
        progress=obj.progress,
        due_date=obj.due_date,
        reminder_frequency=obj.reminder_frequency,
        indicators=indicator_responses,
        actions=action_responses,
        created_at=obj.created_at,
    )


@router.put("/{objective_id}", response_model=ObjectiveResponse)
async def update_objective(
    objective_id: int,
    objective_data: ObjectiveUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update an objective."""
    objective_repo = ObjectiveRepository(db)
    obj = await objective_repo.get_by_id(objective_id)

    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objective not found",
        )

    update_data = objective_data.model_dump(exclude_unset=True)
    obj = await objective_repo.update(obj, update_data)
    obj = await objective_repo.get_by_id_with_relations(obj.id)

    indicators = [IndicatorResponse.model_validate(i) for i in obj.indicators]
    actions = [ActionResponse.model_validate(a) for a in obj.actions]

    return ObjectiveResponse(
        id=obj.id,
        pai_id=obj.pai_id,
        beneficiary_id=obj.beneficiary_id,
        beneficiary_name=obj.beneficiary.full_name if obj.beneficiary else None,
        title=obj.title,
        description=obj.description,
        objective_type=obj.objective_type,
        term=obj.term,
        priority=obj.priority,
        status=obj.status,
        progress=obj.progress,
        due_date=obj.due_date,
        reminder_frequency=obj.reminder_frequency,
        indicators=indicators,
        actions=actions,
        created_at=obj.created_at,
    )


@router.patch("/{objective_id}/progress", response_model=ObjectiveResponse)
async def update_objective_progress(
    objective_id: int,
    progress_data: ObjectiveProgressUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update objective progress."""
    objective_repo = ObjectiveRepository(db)
    obj = await objective_repo.get_by_id(objective_id)

    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objective not found",
        )

    obj = await objective_repo.update_progress(obj, progress_data.progress)
    obj = await objective_repo.get_by_id_with_relations(obj.id)

    indicators = [IndicatorResponse.model_validate(i) for i in obj.indicators]
    actions = [ActionResponse.model_validate(a) for a in obj.actions]

    return ObjectiveResponse(
        id=obj.id,
        pai_id=obj.pai_id,
        beneficiary_id=obj.beneficiary_id,
        beneficiary_name=obj.beneficiary.full_name if obj.beneficiary else None,
        title=obj.title,
        description=obj.description,
        objective_type=obj.objective_type,
        term=obj.term,
        priority=obj.priority,
        status=obj.status,
        progress=obj.progress,
        due_date=obj.due_date,
        reminder_frequency=obj.reminder_frequency,
        indicators=indicators,
        actions=actions,
        created_at=obj.created_at,
    )


@router.patch("/{objective_id}/status", response_model=ObjectiveResponse)
async def update_objective_status(
    objective_id: int,
    status_data: ObjectiveStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update objective status."""
    objective_repo = ObjectiveRepository(db)
    obj = await objective_repo.get_by_id(objective_id)

    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objective not found",
        )

    obj = await objective_repo.update_status(obj, status_data.status)
    obj = await objective_repo.get_by_id_with_relations(obj.id)

    indicators = [IndicatorResponse.model_validate(i) for i in obj.indicators]
    actions = [ActionResponse.model_validate(a) for a in obj.actions]

    return ObjectiveResponse(
        id=obj.id,
        pai_id=obj.pai_id,
        beneficiary_id=obj.beneficiary_id,
        beneficiary_name=obj.beneficiary.full_name if obj.beneficiary else None,
        title=obj.title,
        description=obj.description,
        objective_type=obj.objective_type,
        term=obj.term,
        priority=obj.priority,
        status=obj.status,
        progress=obj.progress,
        due_date=obj.due_date,
        reminder_frequency=obj.reminder_frequency,
        indicators=indicators,
        actions=actions,
        created_at=obj.created_at,
    )


# Action endpoints
@router.get("/{objective_id}/actions", response_model=list[ActionResponse])
async def list_actions(
    objective_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """List all actions for an objective."""
    objective_repo = ObjectiveRepository(db)
    obj = await objective_repo.get_by_id_with_relations(objective_id)

    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objective not found",
        )

    return [ActionResponse.model_validate(a) for a in obj.actions]


@router.post(
    "/{objective_id}/actions",
    response_model=ActionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_action(
    objective_id: int,
    action_data: ActionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Create a new action for an objective."""
    objective_repo = ObjectiveRepository(db)
    obj = await objective_repo.get_by_id(objective_id)

    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objective not found",
        )

    action = await objective_repo.create_action(
        objective_id=objective_id,
        data=action_data.model_dump(),
    )

    return ActionResponse.model_validate(action)


@router.put("/{objective_id}/actions/{action_id}", response_model=ActionResponse)
async def update_action(
    objective_id: int,
    action_id: int,
    action_data: ActionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update an action."""
    objective_repo = ObjectiveRepository(db)
    action = await objective_repo.get_action_by_id(action_id)

    if not action or action.objective_id != objective_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )

    action = await objective_repo.update_action(
        action=action,
        data=action_data.model_dump(exclude_unset=True),
    )

    return ActionResponse.model_validate(action)


@router.delete(
    "/{objective_id}/actions/{action_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_action(
    objective_id: int,
    action_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Delete an action."""
    objective_repo = ObjectiveRepository(db)
    action = await objective_repo.get_action_by_id(action_id)

    if not action or action.objective_id != objective_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found",
        )

    await objective_repo.delete_action(action)


# Indicator endpoints
@router.post(
    "/{objective_id}/indicators/{indicator_id}/achieve",
    response_model=IndicatorResponse,
)
async def achieve_indicator(
    objective_id: int,
    indicator_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Mark an indicator as achieved."""
    objective_repo = ObjectiveRepository(db)
    indicator = await objective_repo.get_indicator_by_id(indicator_id)

    if not indicator or indicator.objective_id != objective_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicator not found",
        )

    indicator = await objective_repo.achieve_indicator(indicator)
    return IndicatorResponse.model_validate(indicator)
