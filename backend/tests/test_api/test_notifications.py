"""Tests for notification endpoints (/api/v1/notifications/*)."""

from httpx import AsyncClient

# ── List notifications ───────────────────────────────────────────────────────


class TestListNotifications:
    """GET /api/v1/notifications"""

    async def test_list_notifications(
        self, client: AsyncClient, msp_headers, test_notifications
    ):
        """List notifications for the current user."""
        response = await client.get(
            "/api/v1/notifications", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 5
        assert len(data["items"]) == 5

    async def test_list_notifications_pagination(
        self, client: AsyncClient, msp_headers, test_notifications
    ):
        """Pagination works correctly."""
        response = await client.get(
            "/api/v1/notifications?page=1&size=2", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["pages"] == 3

    async def test_list_notifications_unread_only(
        self, client: AsyncClient, msp_headers, test_notifications
    ):
        """Filter to unread notifications only."""
        response = await client.get(
            "/api/v1/notifications?unread_only=true", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        # 3 out of 5 are unread (indices 2, 3, 4)
        assert data["total"] == 3
        assert all(item["is_read"] is False for item in data["items"])

    async def test_list_notifications_empty_for_new_user(
        self, client: AsyncClient, admin_headers
    ):
        """A user with no notifications gets an empty list."""
        response = await client.get(
            "/api/v1/notifications", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_notifications_unauthenticated(self, client: AsyncClient):
        """Unauthenticated returns 401."""
        response = await client.get("/api/v1/notifications")
        assert response.status_code == 401


# ── Unread count ─────────────────────────────────────────────────────────────


class TestUnreadCount:
    """GET /api/v1/notifications/unread-count"""

    async def test_unread_count(
        self, client: AsyncClient, msp_headers, test_notifications
    ):
        """Returns the correct number of unread notifications."""
        response = await client.get(
            "/api/v1/notifications/unread-count", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3  # 3 unread out of 5

    async def test_unread_count_zero(
        self, client: AsyncClient, admin_headers
    ):
        """User with no notifications has count 0."""
        response = await client.get(
            "/api/v1/notifications/unread-count", headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json()["count"] == 0


# ── Mark as read ─────────────────────────────────────────────────────────────


class TestMarkAsRead:
    """POST /api/v1/notifications/{id}/read"""

    async def test_mark_as_read(
        self, client: AsyncClient, msp_headers, test_notifications
    ):
        """Mark a specific notification as read."""
        # Pick the first unread notification (index 2 in fixture)
        unread = [n for n in test_notifications if not n.is_read][0]

        response = await client.post(
            f"/api/v1/notifications/{unread.id}/read",
            headers=msp_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_read"] is True
        assert data["id"] == unread.id

    async def test_mark_as_read_not_found(
        self, client: AsyncClient, msp_headers
    ):
        """Non-existent notification returns 404."""
        response = await client.post(
            "/api/v1/notifications/99999/read", headers=msp_headers
        )
        assert response.status_code == 404

    async def test_mark_as_read_other_user(
        self, client: AsyncClient, admin_headers, test_notifications
    ):
        """Cannot mark another user's notification as read (returns 404)."""
        # test_notifications belong to msp_user, admin cannot see them
        notification = test_notifications[0]
        response = await client.post(
            f"/api/v1/notifications/{notification.id}/read",
            headers=admin_headers,
        )
        assert response.status_code == 404


# ── Mark all as read ─────────────────────────────────────────────────────────


class TestMarkAllAsRead:
    """POST /api/v1/notifications/read-all"""

    async def test_mark_all_as_read(
        self, client: AsyncClient, msp_headers, test_notifications
    ):
        """Mark all notifications as read."""
        response = await client.post(
            "/api/v1/notifications/read-all", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        # "3 notifications marked as read" (the 3 unread ones)
        assert "3" in data["message"]

        # Verify all are now read
        count_resp = await client.get(
            "/api/v1/notifications/unread-count", headers=msp_headers
        )
        assert count_resp.json()["count"] == 0

    async def test_mark_all_as_read_idempotent(
        self, client: AsyncClient, msp_headers, test_notifications
    ):
        """Calling mark-all-as-read twice is safe (idempotent)."""
        await client.post(
            "/api/v1/notifications/read-all", headers=msp_headers
        )
        response = await client.post(
            "/api/v1/notifications/read-all", headers=msp_headers
        )
        assert response.status_code == 200
        assert "0" in response.json()["message"]

    async def test_mark_all_as_read_unauthenticated(self, client: AsyncClient):
        """Unauthenticated returns 401."""
        response = await client.post("/api/v1/notifications/read-all")
        assert response.status_code == 401
