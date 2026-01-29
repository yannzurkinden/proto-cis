"""Tests for authentication endpoints (/api/v1/auth/*)."""

import pytest
from httpx import AsyncClient


# ── Login ────────────────────────────────────────────────────────────────────


class TestLogin:
    """POST /api/v1/auth/login"""

    async def test_login_success_with_admin(self, client: AsyncClient, admin_user):
        """Successful login returns an access_token and user info."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.ch", "password": "Admin123!@#abc"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "admin@test.ch"
        assert data["user"]["role"] == "ADMIN"

    async def test_login_success_with_msp(self, client: AsyncClient, msp_user):
        """MSP user can log in and receive a token."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "msp@test.ch", "password": "Msp12345!@#abc"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "MSP"
        assert "expires_in" in data

    async def test_login_wrong_password(self, client: AsyncClient, admin_user):
        """Incorrect password returns 401."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.ch", "password": "WrongPassword1!"},
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Non-existent email returns 401."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@test.ch", "password": "SomePassword1!"},
        )
        assert response.status_code == 401

    async def test_login_inactive_user(self, client: AsyncClient, db_session):
        """Disabled account returns 403."""
        from app.models.user import User
        from app.utils.security import get_password_hash

        user = User(
            email="inactive@test.ch",
            hashed_password=get_password_hash("Inactive123!@#"),
            first_name="Inactive",
            last_name="User",
            role="MSP",
            is_active=False,
        )
        db_session.add(user)
        await db_session.flush()

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@test.ch", "password": "Inactive123!@#"},
        )
        assert response.status_code == 403

    async def test_login_missing_fields(self, client: AsyncClient):
        """Missing required fields returns 422."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@test.ch"},
        )
        assert response.status_code == 422

    async def test_login_returns_user_with_unit_info(
        self, client: AsyncClient, msp_user, test_unit
    ):
        """Login response includes the user's unit information."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "msp@test.ch", "password": "Msp12345!@#abc"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["unit_id"] == test_unit.id


# ── Change password ──────────────────────────────────────────────────────────


class TestChangePassword:
    """POST /api/v1/auth/change-password"""

    async def test_change_password_success(
        self, client: AsyncClient, admin_headers, admin_user
    ):
        """Password change with correct current password succeeds."""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=admin_headers,
            json={
                "current_password": "Admin123!@#abc",
                "new_password": "NewPassword1!@#",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    async def test_change_password_wrong_current(
        self, client: AsyncClient, admin_headers
    ):
        """Wrong current password returns 400."""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=admin_headers,
            json={
                "current_password": "WrongPassword1!",
                "new_password": "NewPassword1!@#",
            },
        )
        assert response.status_code == 400

    async def test_change_password_weak_new(
        self, client: AsyncClient, admin_headers, admin_user
    ):
        """A new password that fails strength validation returns 400."""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=admin_headers,
            json={
                "current_password": "Admin123!@#abc",
                "new_password": "short",  # too short
            },
        )
        assert response.status_code == 422  # pydantic validation (min_length=12)

    async def test_change_password_unauthenticated(self, client: AsyncClient):
        """Unauthenticated request returns 403."""
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "x",
                "new_password": "y",
            },
        )
        assert response.status_code == 403


# ── Logout ───────────────────────────────────────────────────────────────────


class TestLogout:
    """POST /api/v1/auth/logout"""

    async def test_logout_success(self, client: AsyncClient, admin_headers):
        """Authenticated user can log out."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logout successful"

    async def test_logout_unauthenticated(self, client: AsyncClient):
        """Unauthenticated logout returns 403."""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 403


# ── Forgot password ──────────────────────────────────────────────────────────


class TestForgotPassword:
    """POST /api/v1/auth/forgot-password"""

    async def test_forgot_password_existing_user(
        self, client: AsyncClient, admin_user
    ):
        """Returns 200 regardless of whether the email exists (anti-enumeration)."""
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "admin@test.ch"},
        )
        assert response.status_code == 200

    async def test_forgot_password_nonexistent_user(self, client: AsyncClient):
        """Returns 200 even for unknown email (anti-enumeration)."""
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "unknown@test.ch"},
        )
        assert response.status_code == 200


# ── Protected endpoints ──────────────────────────────────────────────────────


class TestProtectedEndpoints:
    """Verify that protected endpoints reject unauthenticated requests."""

    async def test_no_token_returns_403(self, client: AsyncClient):
        """GET /api/v1/users/me without a token returns 403."""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 403

    async def test_invalid_token_returns_401(self, client: AsyncClient):
        """An invalid JWT returns 401."""
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )
        assert response.status_code == 401

    async def test_expired_token(self, client: AsyncClient, admin_user):
        """An expired token returns 401."""
        from datetime import timedelta

        from app.utils.security import create_access_token

        expired_token = create_access_token(
            data={"sub": str(admin_user.id)},
            expires_delta=timedelta(seconds=-10),
        )
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401


# ── Health check (smoke) ─────────────────────────────────────────────────────


class TestHealthCheck:
    """Verify the unauthenticated health endpoints work."""

    async def test_health(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_health_detailed(self, client: AsyncClient):
        response = await client.get("/health/detailed")
        assert response.status_code == 200
        assert "components" in response.json()
