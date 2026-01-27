"""Unit management endpoints."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.repositories.unit_repository import UnitRepository
from app.schemas.unit import UnitCreate, UnitUpdate, UnitResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UnitResponse])
async def list_units(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = None,
):
    """List all units with filtering and pagination."""
    unit_repo = UnitRepository(db)
    skip = (page - 1) * size

    units, total = await unit_repo.get_all_filtered(
        skip=skip,
        limit=size,
        is_active=is_active,
    )

    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedResponse(
        items=[UnitResponse.model_validate(unit) for unit in units],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{unit_id}", response_model=UnitResponse)
async def get_unit(
    unit_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a specific unit by ID."""
    unit_repo = UnitRepository(db)
    unit = await unit_repo.get_by_id(unit_id)

    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found",
        )

    return UnitResponse.model_validate(unit)


@router.post("", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    unit_data: UnitCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    """Create a new unit (admin only)."""
    unit_repo = UnitRepository(db)

    # Check if name already exists
    existing_unit = await unit_repo.get_by_name(unit_data.name)
    if existing_unit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit name already exists",
        )

    unit = await unit_repo.create(unit_data.model_dump())
    return UnitResponse.model_validate(unit)


@router.put("/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    unit_data: UnitUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    """Update a unit (admin only)."""
    unit_repo = UnitRepository(db)
    unit = await unit_repo.get_by_id(unit_id)

    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found",
        )

    # Check if name already exists for another unit
    if unit_data.name and unit_data.name != unit.name:
        existing_unit = await unit_repo.get_by_name(unit_data.name)
        if existing_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit name already exists",
            )

    update_data = unit_data.model_dump(exclude_unset=True)
    unit = await unit_repo.update(unit, update_data)
    return UnitResponse.model_validate(unit)
