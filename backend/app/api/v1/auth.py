"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    LoginRequest,
    Token,
    RefreshResponse,
    PasswordChange,
    ForgotPassword,
    PasswordReset,
    UserMeResponse,
)
from app.schemas.common import Message
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    validate_password_strength,
)

router = APIRouter()
settings = get_settings()
security = HTTPBearer(auto_error=False)


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate user and return tokens."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(login_data.email)

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # Update last login
    await user_repo.update_last_login(user)

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    # Get unit name if applicable
    unit_name = None
    if user.unit_id:
        user_with_unit = await user_repo.get_by_id_with_unit(user.id)
        if user_with_unit and user_with_unit.unit:
            unit_name = user_with_unit.unit.name

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserMeResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            unit_id=user.unit_id,
            unit_name=unit_name,
            is_active=user.is_active,
        ),
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
):
    """Refresh access token using refresh token from cookie."""
    # Try to get refresh token from cookie first, then from header
    from fastapi import Request
    # Note: In a real implementation, you'd get this from the request context
    # For now, we'll use the authorization header as fallback

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided",
        )

    payload = decode_refresh_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(user_id))

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return RefreshResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/logout", response_model=Message)
async def logout(
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Logout user by clearing refresh token cookie."""
    response.delete_cookie("refresh_token")
    return Message(message="Logout successful")


@router.post("/change-password", response_model=Message)
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Change user's password."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Validate new password strength
    is_valid, error_message = validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    user_repo = UserRepository(db)
    hashed_password = get_password_hash(password_data.new_password)
    await user_repo.update_password(current_user, hashed_password)

    return Message(message="Password changed successfully")


@router.post("/forgot-password", response_model=Message)
async def forgot_password(
    data: ForgotPassword,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Request password reset email."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(data.email)

    # Always return success to prevent email enumeration
    if user:
        # TODO: Send password reset email
        pass

    return Message(message="If an account with that email exists, a reset link has been sent")


@router.post("/reset-password", response_model=Message)
async def reset_password(
    data: PasswordReset,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Reset password using reset token."""
    # TODO: Implement proper token verification
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset not yet implemented",
    )
