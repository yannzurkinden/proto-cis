"""Tests for dashboard endpoints (/api/v1/dashboard/*)."""

from httpx import AsyncClient

# ── MSP Dashboard ────────────────────────────────────────────────────────────


class TestMSPDashboard:
    """GET /api/v1/dashboard/msp"""

    async def test_msp_dashboard_success(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """MSP receives their dashboard data."""
        response = await client.get(
            "/api/v1/dashboard/msp", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "my_beneficiaries" in data
        assert "today_reminders" in data
        assert "recent_journal_entries" in data
        assert "pending_tasks" in data

    async def test_msp_dashboard_contains_beneficiary(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """Dashboard includes the MSP's assigned beneficiary."""
        response = await client.get(
            "/api/v1/dashboard/msp", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        names = [b["name"] for b in data["my_beneficiaries"]]
        assert "Jean Dupont" in names

    async def test_msp_dashboard_admin_can_access(
        self, client: AsyncClient, admin_headers
    ):
        """ADMIN can also access the MSP dashboard (they are an authenticated user)."""
        response = await client.get(
            "/api/v1/dashboard/msp", headers=admin_headers
        )
        assert response.status_code == 200

    async def test_msp_dashboard_unauthenticated(self, client: AsyncClient):
        """Unauthenticated returns 401."""
        response = await client.get("/api/v1/dashboard/msp")
        assert response.status_code == 401


# ── Management Dashboard ─────────────────────────────────────────────────────


class TestManagementDashboard:
    """GET /api/v1/dashboard/management"""

    async def test_management_dashboard_as_admin(
        self, client: AsyncClient, admin_headers, test_beneficiary
    ):
        """ADMIN can access the management dashboard."""
        response = await client.get(
            "/api/v1/dashboard/management", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "objectives_overview" in data
        assert "absence_stats" in data
        assert "alerts" in data
        # Summary structure
        summary = data["summary"]
        assert "total_beneficiaries" in summary
        assert "active_beneficiaries" in summary
        assert "new_this_month" in summary
        assert "exited_this_month" in summary

    async def test_management_dashboard_as_res(
        self, client: AsyncClient, res_headers, test_beneficiary
    ):
        """RES can access the management dashboard."""
        response = await client.get(
            "/api/v1/dashboard/management", headers=res_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data

    async def test_management_dashboard_requires_management_role(
        self, client: AsyncClient, msp_headers
    ):
        """MSP cannot access the management dashboard."""
        response = await client.get(
            "/api/v1/dashboard/management", headers=msp_headers
        )
        assert response.status_code == 403

    async def test_management_dashboard_consult_forbidden(
        self, client: AsyncClient, consult_headers
    ):
        """CONSULT cannot access the management dashboard."""
        response = await client.get(
            "/api/v1/dashboard/management", headers=consult_headers
        )
        assert response.status_code == 403

    async def test_management_dashboard_unauthenticated(self, client: AsyncClient):
        """Unauthenticated returns 401."""
        response = await client.get("/api/v1/dashboard/management")
        assert response.status_code == 401

    async def test_management_dashboard_objectives_overview(
        self, client: AsyncClient, admin_headers, test_beneficiary, db_session
    ):
        """Objectives overview contains expected fields."""
        from app.models.objective import Objective

        db_session.add(
            Objective(
                beneficiary_id=test_beneficiary.id,
                title="Dashboard obj",
                objective_type="behavioral",
                term="short",
                status="pending",
            )
        )
        await db_session.flush()

        response = await client.get(
            "/api/v1/dashboard/management", headers=admin_headers
        )
        assert response.status_code == 200
        overview = response.json()["objectives_overview"]
        assert "total" in overview
        assert "overdue" in overview
        assert "achievement_rate" in overview
        assert "achieved_this_month" in overview

    async def test_management_dashboard_with_unit_filter(
        self, client: AsyncClient, admin_headers, test_beneficiary, test_unit
    ):
        """Management dashboard can be filtered by unit_id."""
        response = await client.get(
            f"/api/v1/dashboard/management?unit_id={test_unit.id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
