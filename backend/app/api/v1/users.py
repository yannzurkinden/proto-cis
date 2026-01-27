"""User management endpoints."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin, require_management
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserMeResponse,
)
from app.schemas.common import PaginatedResponse
from app.utils.security import get_password_hash, validate_password_strength

router = APIRouter()


@router.get("/me", response_model=UserMeResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get current authenticated user's information."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id_with_unit(current_user.id)

    unit_name = None
    if user and user.unit:
        unit_name = user.unit.name

    return UserMeResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        unit_id=current_user.unit_id,
        unit_name=unit_name,
        is_active=current_user.is_active,
    )


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    unit_id: Optional[int] = None,
    is_active: Optional[bool] = None,
):
    """List all users with filtering and pagination."""
    user_repo = UserRepository(db)
    skip = (page - 1) * size

    users, total = await user_repo.get_all_filtered(
        skip=skip,
        limit=size,
        role=role,
        unit_id=unit_id,
        is_active=is_active,
    )

    # Build response with unit names
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


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
):
    """Get a specific user by ID."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id_with_unit(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

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


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin)],
):
    """Create a new user (admin only)."""
    user_repo = UserRepository(db)

    # Check if email already exists
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Validate password strength
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    # Create user
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


@router.put("/{user_id}", response_model=UserResponse)
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

    # Check if email already exists for another user
    if user_data.email and user_data.email != user.email:
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Update user
    update_data = user_data.model_dump(exclude_unset=True)
    user = await user_repo.update(user, update_data)

    # Reload with unit
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
