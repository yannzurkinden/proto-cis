"""Tests for user management endpoints (/api/v1/users/*)."""

from httpx import AsyncClient

# ── Get current user (me) ────────────────────────────────────────────────────


class TestGetMe:
    """GET /api/v1/users/me"""

    async def test_get_me_as_admin(self, client: AsyncClient, admin_headers, admin_user):
        """Admin can fetch their own profile."""
        response = await client.get("/api/v1/users/me", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.ch"
        assert data["role"] == "ADMIN"
        assert data["is_active"] is True

    async def test_get_me_as_msp(self, client: AsyncClient, msp_headers, msp_user, test_unit):
        """MSP can fetch their own profile, including unit information."""
        response = await client.get("/api/v1/users/me", headers=msp_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "msp@test.ch"
        assert data["role"] == "MSP"
        assert data["unit_id"] == test_unit.id

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        """Unauthenticated returns 401."""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401


# ── List users ───────────────────────────────────────────────────────────────


class TestListUsers:
    """GET /api/v1/users"""

    async def test_list_users_as_admin(
        self, client: AsyncClient, admin_headers, admin_user, msp_user
    ):
        """ADMIN can list all users."""
        response = await client.get("/api/v1/users", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 2

    async def test_list_users_as_res(
        self, client: AsyncClient, res_headers, res_user, msp_user
    ):
        """RES (management) can list users."""
        response = await client.get("/api/v1/users", headers=res_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    async def test_list_users_as_msp_forbidden(
        self, client: AsyncClient, msp_headers
    ):
        """MSP cannot list users (require_management)."""
        response = await client.get("/api/v1/users", headers=msp_headers)
        assert response.status_code == 403

    async def test_list_users_filter_by_role(
        self, client: AsyncClient, admin_headers, admin_user, msp_user
    ):
        """Filter users by role."""
        response = await client.get(
            "/api/v1/users?role=MSP", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(item["role"] == "MSP" for item in data["items"])

    async def test_list_users_filter_by_active(
        self, client: AsyncClient, admin_headers, admin_user
    ):
        """Filter users by is_active."""
        response = await client.get(
            "/api/v1/users?is_active=true", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(item["is_active"] is True for item in data["items"])

    async def test_list_users_pagination(
        self, client: AsyncClient, admin_headers, admin_user, msp_user
    ):
        """Pagination works correctly."""
        response = await client.get(
            "/api/v1/users?page=1&size=1", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] >= 2


# ── Get user ─────────────────────────────────────────────────────────────────


class TestGetUser:
    """GET /api/v1/users/{id}"""

    async def test_get_user_as_admin(
        self, client: AsyncClient, admin_headers, msp_user
    ):
        """ADMIN can fetch any user by ID."""
        response = await client.get(
            f"/api/v1/users/{msp_user.id}", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == msp_user.id
        assert data["email"] == "msp@test.ch"
        assert data["role"] == "MSP"

    async def test_get_user_as_res(
        self, client: AsyncClient, res_headers, msp_user
    ):
        """RES can fetch a user by ID."""
        response = await client.get(
            f"/api/v1/users/{msp_user.id}", headers=res_headers
        )
        assert response.status_code == 200

    async def test_get_user_not_found(
        self, client: AsyncClient, admin_headers
    ):
        """Non-existent user ID returns 404."""
        response = await client.get("/api/v1/users/99999", headers=admin_headers)
        assert response.status_code == 404

    async def test_get_user_as_msp_forbidden(
        self, client: AsyncClient, msp_headers, admin_user
    ):
        """MSP cannot get another user's details (require_management)."""
        response = await client.get(
            f"/api/v1/users/{admin_user.id}", headers=msp_headers
        )
        assert response.status_code == 403


# ── Create user ──────────────────────────────────────────────────────────────


class TestCreateUser:
    """POST /api/v1/users"""

    async def test_create_user_as_admin(
        self, client: AsyncClient, admin_headers
    ):
        """ADMIN can create a new user."""
        response = await client.post(
            "/api/v1/users",
            headers=admin_headers,
            json={
                "email": "new_user@test.ch",
                "password": "NewUser123!@#ab",
                "first_name": "New",
                "last_name": "User",
                "role": "MSP",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new_user@test.ch"
        assert data["role"] == "MSP"
        assert data["is_active"] is True
        assert "id" in data

    async def test_create_user_duplicate_email(
        self, client: AsyncClient, admin_headers, admin_user
    ):
        """Duplicate email returns 400."""
        response = await client.post(
            "/api/v1/users",
            headers=admin_headers,
            json={
                "email": "admin@test.ch",
                "password": "Duplicate123!@#a",
                "first_name": "Dup",
                "last_name": "User",
                "role": "MSP",
            },
        )
        assert response.status_code == 400

    async def test_create_user_weak_password(
        self, client: AsyncClient, admin_headers
    ):
        """Password not meeting strength rules returns 400."""
        response = await client.post(
            "/api/v1/users",
            headers=admin_headers,
            json={
                "email": "weak@test.ch",
                "password": "weakpassword!",  # no uppercase or digit (actually has lowercase)
                "first_name": "Weak",
                "last_name": "Pass",
                "role": "MSP",
            },
        )
        # Either 400 (custom validation) or 422 (pydantic) depending on flow
        assert response.status_code in [400, 422]

    async def test_create_user_as_msp_forbidden(
        self, client: AsyncClient, msp_headers
    ):
        """MSP cannot create users (require_admin)."""
        response = await client.post(
            "/api/v1/users",
            headers=msp_headers,
            json={
                "email": "nope@test.ch",
                "password": "NopePass123!@#a",
                "first_name": "Nope",
                "last_name": "User",
                "role": "MSP",
            },
        )
        assert response.status_code == 403

    async def test_create_user_as_res_forbidden(
        self, client: AsyncClient, res_headers
    ):
        """RES cannot create users (require_admin)."""
        response = await client.post(
            "/api/v1/users",
            headers=res_headers,
            json={
                "email": "nope2@test.ch",
                "password": "NopePass123!@#a",
                "first_name": "Nope",
                "last_name": "Two",
                "role": "MSP",
            },
        )
        assert response.status_code == 403

    async def test_create_user_missing_fields(
        self, client: AsyncClient, admin_headers
    ):
        """Missing required fields returns 422."""
        response = await client.post(
            "/api/v1/users",
            headers=admin_headers,
            json={"email": "incomplete@test.ch"},
        )
        assert response.status_code == 422


# ── Update user ──────────────────────────────────────────────────────────────


class TestUpdateUser:
    """PUT /api/v1/users/{id}"""

    async def test_update_user_as_admin(
        self, client: AsyncClient, admin_headers, msp_user
    ):
        """ADMIN can update another user's profile."""
        response = await client.put(
            f"/api/v1/users/{msp_user.id}",
            headers=admin_headers,
            json={"first_name": "Updated", "role": "RES"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["role"] == "RES"

    async def test_update_user_deactivate(
        self, client: AsyncClient, admin_headers, msp_user
    ):
        """ADMIN can deactivate a user."""
        response = await client.put(
            f"/api/v1/users/{msp_user.id}",
            headers=admin_headers,
            json={"is_active": False},
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    async def test_update_user_not_found(
        self, client: AsyncClient, admin_headers
    ):
        """Non-existent user returns 404."""
        response = await client.put(
            "/api/v1/users/99999",
            headers=admin_headers,
            json={"first_name": "Ghost"},
        )
        assert response.status_code == 404

    async def test_update_user_as_msp_forbidden(
        self, client: AsyncClient, msp_headers, admin_user
    ):
        """MSP cannot update users (require_admin)."""
        response = await client.put(
            f"/api/v1/users/{admin_user.id}",
            headers=msp_headers,
            json={"first_name": "Hacked"},
        )
        assert response.status_code == 403

    async def test_update_user_duplicate_email(
        self, client: AsyncClient, admin_headers, msp_user, admin_user
    ):
        """Changing email to an existing one returns 400."""
        response = await client.put(
            f"/api/v1/users/{msp_user.id}",
            headers=admin_headers,
            json={"email": "admin@test.ch"},
        )
        assert response.status_code == 400
