"""Admin endpoints for journal categories and audit logs."""

from datetime import date, datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin, require_management
from app.models.user import User
from app.repositories.journal_repository import JournalRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.common import PaginatedResponse
from app.schemas.journal import JournalCategoryResponse

from pydantic import BaseModel, ConfigDict, Field

router = APIRouter()


# --- Admin schemas ---


class JournalCategoryCreate(BaseModel):
    """Schema for creating a journal category."""

    name: str = Field(..., max_length=50)
    label: str = Field(..., max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)


class JournalCategoryUpdate(BaseModel):
    """Schema for updating a journal category."""

    name: Optional[str] = Field(None, max_length=50)
    label: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


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
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    """List audit logs with filtering (admin only)."""
    notification_repo = NotificationRepository(db)
    skip = (page - 1) * size

    logs, total = await notification_repo.get_audit_logs(
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
