"""Admin endpoints for user management, units, skills, journal categories, and audit logs."""

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import require_admin, require_management
from app.models.beneficiary import Beneficiary
from app.models.user import User
from app.repositories.journal_repository import JournalRepository
from app.repositories.notification_repository import AuditLogRepository
from app.repositories.skill_repository import SkillRepository
from app.repositories.unit_repository import UnitRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.journal import JournalCategoryResponse
from app.schemas.skill import SkillCreate, SkillResponse, SkillUpdate
from app.schemas.unit import UnitCreate, UnitResponse, UnitUpdate
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.utils.security import get_password_hash, validate_password_strength

router = APIRouter()


# --- Admin schemas ---


class JournalCategoryCreate(BaseModel):
    """Schema for creating a journal category."""

    name: str = Field(..., max_length=50)
    label: str = Field(..., max_length=100)
    color: str | None = Field(None, max_length=7)
    icon: str | None = Field(None, max_length=50)


class JournalCategoryUpdate(BaseModel):
    """Schema for updating a journal category."""

    name: str | None = Field(None, max_length=50)
    label: str | None = Field(None, max_length=100)
    color: str | None = Field(None, max_length=7)
    icon: str | None = Field(None, max_length=50)
    is_active: bool | None = None
    sort_order: int | None = None


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    action: str
    resource_type: str
    resource_id: int | None = None
    old_values: dict | None = None
    new_values: dict | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime


class UnitStatsResponse(BaseModel):
    """Schema for unit statistics."""

    beneficiary_count: int
    msp_count: int


# --- User Management Endpoints ---


@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    role: str | None = None,
    unit_id: int | None = None,
    is_active: bool | None = None,
    search: str | None = None,
):
    """List all users with filtering, search, and pagination."""
    query = select(User).options(selectinload(User.unit))

    if role:
        query = query.where(User.role == role)
    if unit_id:
        query = query.where(User.unit_id == unit_id)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.email.ilike(search_term),
            )
        )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginated
    skip = (page - 1) * size
    query = query.offset(skip).limit(size).order_by(User.last_name, User.first_name)
    result = await db.execute(query)
    users = list(result.scalars().all())

    items = []
    for user in users:
        unit_name = user.unit.name if user.unit else None
        items.append(
            UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
                unit_id=user.unit_id,
                unit_name=unit_name,
                is_active=user.is_active,
                last_login=user.last_login,
                created_at=user.created_at,
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


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    """Create a new user (admin only)."""
    user_repo = UserRepository(db)

    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    user_dict = user_data.model_dump(exclude={"password"})
    user_dict["hashed_password"] = get_password_hash(user_data.password)

    user = await user_repo.create(user_dict)

    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        unit_id=user.unit_id,
        unit_name=None,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at,
    )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    """Update a user (admin only)."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_data.email and user_data.email != user.email:
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    update_data = user_data.model_dump(exclude_unset=True)
    user = await user_repo.update(user, update_data)

    user = await user_repo.get_by_id_with_unit(user.id)
    unit_name = user.unit.name if user.unit else None

    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        unit_id=user.unit_id,
        unit_name=unit_name,
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at,
    )


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    """Deactivate a user (admin only)."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    await user_repo.update(user, {"is_active": False})
    return {"detail": "User deactivated"}


# --- Unit Management Endpoints ---


@router.get("/units", response_model=list[UnitResponse])
async def list_units(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
):
    """List all units."""
    unit_repo = UnitRepository(db)
    units = await unit_repo.get_all_active()
    return [UnitResponse.model_validate(u) for u in units]


@router.post("/units", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    unit_data: UnitCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    """Create a new unit (admin only)."""
    unit_repo = UnitRepository(db)

    existing_unit = await unit_repo.get_by_name(unit_data.name)
    if existing_unit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit name already exists",
        )

    unit = await unit_repo.create(unit_data.model_dump())
    return UnitResponse.model_validate(unit)


@router.put("/units/{unit_id}", response_model=UnitResponse)
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


@router.get("/units/{unit_id}/stats", response_model=UnitStatsResponse)
async def get_unit_stats(
    unit_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
):
    """Get statistics for a unit."""
    unit_repo = UnitRepository(db)
    unit = await unit_repo.get_by_id(unit_id)

    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found",
        )

    # Count beneficiaries in this unit
    ben_count = (await db.execute(
        select(func.count()).select_from(Beneficiary).where(Beneficiary.unit_id == unit_id)
    )).scalar() or 0

    # Count MSPs in this unit
    msp_count = (await db.execute(
        select(func.count()).select_from(User).where(User.unit_id == unit_id, User.role == "MSP")
    )).scalar() or 0

    return UnitStatsResponse(beneficiary_count=ben_count, msp_count=msp_count)


# --- Skill Reference Endpoints ---


@router.get("/skills", response_model=list[SkillResponse])
async def list_skills(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
):
    """List all reference skills."""
    skill_repo = SkillRepository(db)
    skills = await skill_repo.get_all_active()
    return [SkillResponse.model_validate(s) for s in skills]


@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
):
    """Create a new reference skill."""
    skill_repo = SkillRepository(db)
    skill = await skill_repo.create(skill_data.model_dump())
    return SkillResponse.model_validate(skill)


@router.put("/skills/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
):
    """Update a reference skill."""
    skill_repo = SkillRepository(db)
    skill = await skill_repo.get_by_id(skill_id)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    update_data = skill_data.model_dump(exclude_unset=True)
    skill = await skill_repo.update(skill, update_data)
    return SkillResponse.model_validate(skill)


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
):
    """Delete (deactivate) a reference skill."""
    skill_repo = SkillRepository(db)
    skill = await skill_repo.get_by_id(skill_id)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    await skill_repo.update(skill, {"is_active": False})


# --- Journal Category Endpoints ---


@router.get("/journal-categories", response_model=list[JournalCategoryResponse])
async def list_journal_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
    active_only: bool = True,
):
    """List all journal categories (management only)."""
    journal_repo = JournalRepository(db)
    categories = await journal_repo.get_all_categories(active_only=active_only)
    return [JournalCategoryResponse.model_validate(c) for c in categories]


@router.post(
    "/journal-categories",
    response_model=JournalCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_journal_category(
    category_data: JournalCategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    """Create a new journal category (admin only)."""
    journal_repo = JournalRepository(db)
    category = await journal_repo.create_category(data=category_data.model_dump())
    return JournalCategoryResponse.model_validate(category)


@router.put(
    "/journal-categories/{category_id}",
    response_model=JournalCategoryResponse,
)
async def update_journal_category(
    category_id: int,
    category_data: JournalCategoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    """Update a journal category (admin only)."""
    journal_repo = JournalRepository(db)
    category = await journal_repo.get_category_by_id(category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal category not found",
        )

    update_data = category_data.model_dump(exclude_unset=True)
    category = await journal_repo.update_category(category, update_data)
    return JournalCategoryResponse.model_validate(category)


# --- Audit Log Endpoints ---


@router.get("/audit-logs", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    """List audit logs with filtering (admin only)."""
    audit_repo = AuditLogRepository(db)
    skip = (page - 1) * size

    logs, total = await audit_repo.get_logs_filtered(
        skip=skip,
        limit=size,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        date_from=date_from,
        date_to=date_to,
    )

    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedResponse(
        items=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )
