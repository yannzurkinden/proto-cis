"""Tests for objective management endpoints (/api/v1/objectives/*)."""

from httpx import AsyncClient

# ── Helpers ──────────────────────────────────────────────────────────────────


def _objective_payload(beneficiary_id: int, **overrides) -> dict:
    """Return a minimal valid objective creation payload."""
    base = {
        "title": "Improve punctuality",
        "description": "Arrive on time every day for one month",
        "objective_type": "behavioral",
        "term": "short",
        "priority": "medium",
        "beneficiary_id": beneficiary_id,
        "due_date": "2024-12-31",
    }
    base.update(overrides)
    return base


# ── Create objective ─────────────────────────────────────────────────────────


class TestCreateObjective:
    """POST /api/v1/objectives"""

    async def test_create_objective_as_msp(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """MSP can create an objective for their beneficiary."""
        payload = _objective_payload(test_beneficiary.id)
        response = await client.post(
            "/api/v1/objectives", headers=msp_headers, json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["beneficiary_id"] == test_beneficiary.id
        assert data["status"] == "pending"
        assert data["progress"] == 0
        assert "id" in data

    async def test_create_objective_with_indicators_and_actions(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """Create objective with inline indicators and actions."""
        payload = _objective_payload(
            test_beneficiary.id,
            indicators=[{"description": "Zero late arrivals in week 1"}],
            actions=[
                {
                    "description": "Set a morning alarm",
                    "responsible": "beneficiary",
                }
            ],
        )
        response = await client.post(
            "/api/v1/objectives", headers=msp_headers, json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data.get("indicators", [])) == 1
        assert len(data.get("actions", [])) == 1

    async def test_create_objective_as_admin(
        self, client: AsyncClient, admin_headers, test_beneficiary
    ):
        """ADMIN can also create objectives."""
        payload = _objective_payload(test_beneficiary.id, title="Admin-created obj")
        response = await client.post(
            "/api/v1/objectives", headers=admin_headers, json=payload
        )
        assert response.status_code == 201

    async def test_create_objective_beneficiary_not_found(
        self, client: AsyncClient, msp_headers
    ):
        """Non-existent beneficiary returns 404."""
        payload = _objective_payload(99999)
        response = await client.post(
            "/api/v1/objectives", headers=msp_headers, json=payload
        )
        assert response.status_code == 404

    async def test_create_objective_missing_fields(
        self, client: AsyncClient, msp_headers
    ):
        """Missing required fields returns 422."""
        response = await client.post(
            "/api/v1/objectives",
            headers=msp_headers,
            json={"title": "Incomplete"},
        )
        assert response.status_code == 422

    async def test_create_objective_consult_forbidden(
        self, client: AsyncClient, consult_headers, test_beneficiary
    ):
        """CONSULT cannot create objectives."""
        payload = _objective_payload(test_beneficiary.id)
        response = await client.post(
            "/api/v1/objectives", headers=consult_headers, json=payload
        )
        assert response.status_code == 403


# ── List objectives ──────────────────────────────────────────────────────────


class TestListObjectives:
    """GET /api/v1/objectives"""

    async def test_list_objectives(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """List objectives returns paginated results."""
        from app.models.objective import Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Test obj",
            objective_type="operational",
            term="medium",
            status="pending",
        )
        db_session.add(obj)
        await db_session.flush()

        response = await client.get("/api/v1/objectives", headers=msp_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    async def test_list_objectives_filter_by_beneficiary(
        self, client: AsyncClient, admin_headers, test_beneficiary, db_session
    ):
        """Filter objectives by beneficiary_id."""
        from app.models.objective import Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Filtered obj",
            objective_type="pai",
            term="long",
            status="in_progress",
        )
        db_session.add(obj)
        await db_session.flush()

        response = await client.get(
            f"/api/v1/objectives?beneficiary_id={test_beneficiary.id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert all(
            item["beneficiary_id"] == test_beneficiary.id for item in data["items"]
        )

    async def test_list_objectives_filter_by_status(
        self, client: AsyncClient, admin_headers, test_beneficiary, db_session
    ):
        """Filter objectives by status."""
        from app.models.objective import Objective

        for s in ["pending", "in_progress", "achieved"]:
            db_session.add(
                Objective(
                    beneficiary_id=test_beneficiary.id,
                    title=f"Obj {s}",
                    objective_type="behavioral",
                    term="short",
                    status=s,
                )
            )
        await db_session.flush()

        response = await client.get(
            "/api/v1/objectives?status=achieved", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == "achieved" for item in data["items"])


# ── Get objective ────────────────────────────────────────────────────────────


class TestGetObjective:
    """GET /api/v1/objectives/{id}"""

    async def test_get_objective(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Fetch an objective by ID."""
        from app.models.objective import Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Specific objective",
            objective_type="pai",
            term="medium",
            status="pending",
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        response = await client.get(
            f"/api/v1/objectives/{obj.id}", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == obj.id
        assert data["title"] == "Specific objective"

    async def test_get_objective_not_found(
        self, client: AsyncClient, msp_headers
    ):
        response = await client.get("/api/v1/objectives/99999", headers=msp_headers)
        assert response.status_code == 404


# ── Update objective ─────────────────────────────────────────────────────────


class TestUpdateObjective:
    """PUT /api/v1/objectives/{id}"""

    async def test_update_objective(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Update an objective's title and priority."""
        from app.models.objective import Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Old title",
            objective_type="behavioral",
            term="short",
            priority="low",
            status="pending",
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        response = await client.put(
            f"/api/v1/objectives/{obj.id}",
            headers=msp_headers,
            json={"title": "New title", "priority": "high"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New title"
        assert data["priority"] == "high"

    async def test_update_objective_not_found(
        self, client: AsyncClient, msp_headers
    ):
        response = await client.put(
            "/api/v1/objectives/99999",
            headers=msp_headers,
            json={"title": "x"},
        )
        assert response.status_code == 404


# ── Update progress ──────────────────────────────────────────────────────────


class TestUpdateProgress:
    """PATCH /api/v1/objectives/{id}/progress"""

    async def test_update_progress(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Set progress to 50 moves status to in_progress."""
        from app.models.objective import Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Progress test",
            objective_type="operational",
            term="short",
            status="pending",
            progress=0,
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        response = await client.patch(
            f"/api/v1/objectives/{obj.id}/progress",
            headers=msp_headers,
            json={"progress": 50},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 50
        assert data["status"] == "in_progress"

    async def test_update_progress_to_100_achieves(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Setting progress to 100 automatically sets status to achieved."""
        from app.models.objective import Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Complete test",
            objective_type="behavioral",
            term="medium",
            status="in_progress",
            progress=80,
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        response = await client.patch(
            f"/api/v1/objectives/{obj.id}/progress",
            headers=msp_headers,
            json={"progress": 100},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 100
        assert data["status"] == "achieved"

    async def test_update_progress_not_found(
        self, client: AsyncClient, msp_headers
    ):
        response = await client.patch(
            "/api/v1/objectives/99999/progress",
            headers=msp_headers,
            json={"progress": 10},
        )
        assert response.status_code == 404

    async def test_update_progress_invalid_value(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Progress > 100 or < 0 returns 422."""
        from app.models.objective import Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Invalid progress",
            objective_type="behavioral",
            term="short",
            status="pending",
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        response = await client.patch(
            f"/api/v1/objectives/{obj.id}/progress",
            headers=msp_headers,
            json={"progress": 150},
        )
        assert response.status_code == 422


# ── Update status ────────────────────────────────────────────────────────────


class TestUpdateStatus:
    """PATCH /api/v1/objectives/{id}/status"""

    async def test_update_status_to_achieved(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Setting status to achieved sets progress to 100."""
        from app.models.objective import Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Status test",
            objective_type="pai",
            term="long",
            status="in_progress",
            progress=60,
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        response = await client.patch(
            f"/api/v1/objectives/{obj.id}/status",
            headers=msp_headers,
            json={"status": "achieved"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "achieved"
        assert data["progress"] == 100

    async def test_update_status_to_abandoned(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Set status to abandoned."""
        from app.models.objective import Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Abandon test",
            objective_type="behavioral",
            term="short",
            status="in_progress",
            progress=20,
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        response = await client.patch(
            f"/api/v1/objectives/{obj.id}/status",
            headers=msp_headers,
            json={"status": "abandoned"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "abandoned"

    async def test_update_status_not_found(
        self, client: AsyncClient, msp_headers
    ):
        response = await client.patch(
            "/api/v1/objectives/99999/status",
            headers=msp_headers,
            json={"status": "achieved"},
        )
        assert response.status_code == 404

    async def test_update_status_invalid(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Invalid status value returns 422."""
        from app.models.objective import Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Invalid status",
            objective_type="behavioral",
            term="short",
            status="pending",
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        response = await client.patch(
            f"/api/v1/objectives/{obj.id}/status",
            headers=msp_headers,
            json={"status": "nonsense"},
        )
        assert response.status_code == 422


# ── Actions sub-resource ─────────────────────────────────────────────────────


class TestActions:
    """CRUD for /api/v1/objectives/{id}/actions"""

    async def test_list_actions(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """List actions for an objective."""
        from app.models.objective import Action, Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Action test",
            objective_type="operational",
            term="short",
            status="pending",
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        action = Action(
            objective_id=obj.id,
            description="Buy an alarm clock",
            responsible="beneficiary",
            status="pending",
        )
        db_session.add(action)
        await db_session.flush()

        response = await client.get(
            f"/api/v1/objectives/{obj.id}/actions", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["description"] == "Buy an alarm clock"

    async def test_create_action(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Create an action for an existing objective."""
        from app.models.objective import Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Action create test",
            objective_type="behavioral",
            term="short",
            status="pending",
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        response = await client.post(
            f"/api/v1/objectives/{obj.id}/actions",
            headers=msp_headers,
            json={
                "description": "Register for training",
                "responsible": "msp",
                "due_date": "2024-10-01",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Register for training"
        assert data["responsible"] == "msp"

    async def test_update_action(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Update an action's status to done."""
        from app.models.objective import Action, Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Action update test",
            objective_type="behavioral",
            term="short",
            status="pending",
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        action = Action(
            objective_id=obj.id,
            description="Pending action",
            status="pending",
        )
        db_session.add(action)
        await db_session.flush()
        await db_session.refresh(action)

        response = await client.put(
            f"/api/v1/objectives/{obj.id}/actions/{action.id}",
            headers=msp_headers,
            json={"status": "done"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "done"

    async def test_delete_action(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Delete an action returns 204."""
        from app.models.objective import Action, Objective

        obj = Objective(
            beneficiary_id=test_beneficiary.id,
            title="Action delete test",
            objective_type="behavioral",
            term="short",
            status="pending",
        )
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)

        action = Action(
            objective_id=obj.id,
            description="To remove",
            status="pending",
        )
        db_session.add(action)
        await db_session.flush()
        await db_session.refresh(action)

        response = await client.delete(
            f"/api/v1/objectives/{obj.id}/actions/{action.id}",
            headers=msp_headers,
        )
        assert response.status_code == 204
