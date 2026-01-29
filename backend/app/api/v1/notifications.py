"""Notification endpoints."""

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.schemas.common import PaginatedResponse, Message

from pydantic import BaseModel, ConfigDict

router = APIRouter()


# --- Notification schemas ---


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    notification_type: str
    title: str
    message: Optional[str] = None
    link: Optional[str] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime


class UnreadCountResponse(BaseModel):
    """Schema for unread notification count."""

    count: int


# --- Notification Endpoints ---


@router.get("", response_model=PaginatedResponse[NotificationResponse])
async def list_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
):
    """List the current user's notifications with pagination."""
    notification_repo = NotificationRepository(db)
    skip = (page - 1) * size

    notifications, total = await notification_repo.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=size,
        unread_only=unread_only,
    )

    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the count of unread notifications for the current user."""
    notification_repo = NotificationRepository(db)
    count = await notification_repo.get_unread_count(user_id=current_user.id)
    return UnreadCountResponse(count=count)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Mark a specific notification as read."""
    notification_repo = NotificationRepository(db)
    notification = await notification_repo.get_notification_by_id(notification_id)

    if not notification or notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification = await notification_repo.mark_as_read(notification)
    return NotificationResponse.model_validate(notification)


@router.post("/read-all", response_model=Message)
async def mark_all_as_read(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Mark all of the current user's notifications as read."""
    notification_repo = NotificationRepository(db)
    count = await notification_repo.mark_all_as_read(user_id=current_user.id)
    return Message(message=f"{count} notifications marked as read")


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Delete a notification."""
    notification_repo = NotificationRepository(db)
    notification = await notification_repo.get_by_id(notification_id)

    if not notification or notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    await notification_repo.delete(notification)
