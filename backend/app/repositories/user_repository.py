"""User repository for database operations."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_unit(self, id: int) -> User | None:
        """Get user by ID with unit relationship loaded."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.unit))
            .where(User.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all_filtered(
        self,
        skip: int = 0,
        limit: int = 20,
        role: str | None = None,
        unit_id: int | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        """Get all users with filtering and pagination."""
        query = select(User).options(selectinload(User.unit))

        if role:
            query = query.where(User.role == role)
        if unit_id:
            query = query.where(User.unit_id == unit_id)
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginated query
        query = query.offset(skip).limit(limit).order_by(User.last_name, User.first_name)
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total

    async def update_last_login(self, user: User) -> User:
        """Update user's last login timestamp."""
        user.last_login = datetime.now(UTC)
        await self.db.flush()
        return user

    async def update_password(self, user: User, hashed_password: str) -> User:
        """Update user's password."""
        user.hashed_password = hashed_password
        user.password_changed_at = datetime.now(UTC)
        await self.db.flush()
        return user
