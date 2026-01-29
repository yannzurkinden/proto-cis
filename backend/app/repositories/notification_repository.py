"""Notification repository for database operations."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import Notification, AuditLog
from app.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Notification)

    async def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Notification], int]:
        """Get notifications for a user with filtering and pagination."""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.is_read == False)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginated query
        query = query.offset(skip).limit(limit).order_by(Notification.created_at.desc())
        result = await self.db.execute(query)
        notifications = list(result.scalars().all())

        return notifications, total

    async def get_unread_count(self, user_id: int) -> int:
        """Get the count of unread notifications for a user."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)
        )
        return result.scalar() or 0

    async def mark_as_read(self, notification_id: int) -> Notification:
        """Mark a notification as read."""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if notification:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            await self.db.flush()
            await self.db.refresh(notification)

        return notification

    async def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user. Returns count of updated notifications."""
        result = await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        await self.db.flush()
        return result.rowcount

    async def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: Optional[str] = None,
        link: Optional[str] = None,
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
        )
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification


class AuditLogRepository:
    """Repository for AuditLog model."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_log(
        self,
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Create a new audit log entry."""
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log

    async def get_logs_filtered(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[AuditLog], int]:
        """Get audit logs with filtering and pagination."""
        query = select(AuditLog)

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if date_from:
            query = query.where(AuditLog.created_at >= date_from)
        if date_to:
            query = query.where(AuditLog.created_at <= date_to)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginated query
        query = query.offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total
