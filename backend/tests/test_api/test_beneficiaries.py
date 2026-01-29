"""Tests for beneficiary management endpoints (/api/v1/beneficiaries/*)."""

import pytest
from httpx import AsyncClient


# ── List beneficiaries ───────────────────────────────────────────────────────


class TestListBeneficiaries:
    """GET /api/v1/beneficiaries"""

    async def test_list_beneficiaries_as_msp(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """MSP sees beneficiaries (filtered to their own)."""
        response = await client.get(
            "/api/v1/beneficiaries", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
        assert data["page"] == 1

    async def test_list_beneficiaries_as_admin(
        self, client: AsyncClient, admin_headers, test_beneficiary
    ):
        """ADMIN sees all beneficiaries."""
        response = await client.get(
            "/api/v1/beneficiaries", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    async def test_list_beneficiaries_pagination(
        self, client: AsyncClient, admin_headers, test_beneficiary, second_beneficiary
    ):
        """Pagination parameters are respected."""
        response = await client.get(
            "/api/v1/beneficiaries?page=1&size=1", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] >= 2
        assert data["pages"] >= 2

    async def test_list_beneficiaries_filter_by_status(
        self, client: AsyncClient, admin_headers, test_beneficiary
    ):
        """Filter by status=active returns matching results."""
        response = await client.get(
            "/api/v1/beneficiaries?status=active", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == "active" for item in data["items"])

    async def test_list_beneficiaries_search(
        self, client: AsyncClient, admin_headers, test_beneficiary
    ):
        """Search by name fragment returns matching results."""
        response = await client.get(
            "/api/v1/beneficiaries?search=Dupont", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any("Dupont" in item["last_name"] for item in data["items"])

    async def test_list_unauthenticated(self, client: AsyncClient):
        """Unauthenticated returns 403."""
        response = await client.get("/api/v1/beneficiaries")
        assert response.status_code == 403


# ── Get single beneficiary ───────────────────────────────────────────────────


class TestGetBeneficiary:
    """GET /api/v1/beneficiaries/{id}"""

    async def test_get_beneficiary(
        self, client: AsyncClient, admin_headers, test_beneficiary
    ):
        """Fetch a beneficiary by ID."""
        response = await client.get(
            f"/api/v1/beneficiaries/{test_beneficiary.id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_beneficiary.id
        assert data["first_name"] == "Jean"
        assert data["last_name"] == "Dupont"
        assert data["status"] == "active"

    async def test_get_beneficiary_not_found(
        self, client: AsyncClient, admin_headers
    ):
        """Non-existent ID returns 404."""
        response = await client.get(
            "/api/v1/beneficiaries/99999", headers=admin_headers
        )
        assert response.status_code == 404

    async def test_get_beneficiary_includes_unit_and_referent(
        self, client: AsyncClient, admin_headers, test_beneficiary, test_unit, msp_user
    ):
        """Response includes unit and referent information."""
        response = await client.get(
            f"/api/v1/beneficiaries/{test_beneficiary.id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["unit_id"] == test_unit.id
        assert data["referent_id"] == msp_user.id


# ── Create beneficiary ──────────────────────────────────────────────────────


class TestCreateBeneficiary:
    """POST /api/v1/beneficiaries"""

    async def test_create_beneficiary_as_msp(
        self, client: AsyncClient, msp_headers, test_unit
    ):
        """MSP can create a beneficiary."""
        response = await client.post(
            "/api/v1/beneficiaries",
            headers=msp_headers,
            json={
                "first_name": "Pierre",
                "last_name": "Blanc",
                "date_of_birth": "1992-06-10",
                "entry_date": "2024-04-01",
                "language": "fr",
                "unit_id": test_unit.id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Pierre"
        assert data["last_name"] == "Blanc"
        assert data["status"] == "active"
        assert "id" in data

    async def test_create_beneficiary_as_admin(
        self, client: AsyncClient, admin_headers
    ):
        """ADMIN can create a beneficiary."""
        response = await client.post(
            "/api/v1/beneficiaries",
            headers=admin_headers,
            json={
                "first_name": "Anne",
                "last_name": "Noir",
                "date_of_birth": "1988-12-25",
                "entry_date": "2024-05-01",
                "language": "de",
            },
        )
        assert response.status_code == 201

    async def test_create_beneficiary_missing_required_fields(
        self, client: AsyncClient, msp_headers
    ):
        """Missing required fields returns 422."""
        response = await client.post(
            "/api/v1/beneficiaries",
            headers=msp_headers,
            json={"first_name": "Only"},
        )
        assert response.status_code == 422

    async def test_create_beneficiary_consult_forbidden(
        self, client: AsyncClient, consult_headers
    ):
        """CONSULT role cannot create a beneficiary (403)."""
        response = await client.post(
            "/api/v1/beneficiaries",
            headers=consult_headers,
            json={
                "first_name": "Nope",
                "last_name": "Nope",
                "date_of_birth": "2000-01-01",
                "entry_date": "2024-01-01",
                "language": "fr",
            },
        )
        assert response.status_code == 403


# ── Update beneficiary ──────────────────────────────────────────────────────


class TestUpdateBeneficiary:
    """PUT /api/v1/beneficiaries/{id}"""

    async def test_update_beneficiary(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """Update basic fields on a beneficiary."""
        response = await client.put(
            f"/api/v1/beneficiaries/{test_beneficiary.id}",
            headers=msp_headers,
            json={"phone": "+41 79 111 22 33", "city": "Lausanne"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+41 79 111 22 33"
        assert data["city"] == "Lausanne"

    async def test_update_beneficiary_status(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """Change beneficiary status to paused."""
        response = await client.put(
            f"/api/v1/beneficiaries/{test_beneficiary.id}",
            headers=msp_headers,
            json={"status": "paused"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "paused"

    async def test_update_beneficiary_not_found(
        self, client: AsyncClient, msp_headers
    ):
        """Updating non-existent beneficiary returns 404."""
        response = await client.put(
            "/api/v1/beneficiaries/99999",
            headers=msp_headers,
            json={"phone": "+41 00 000 00 00"},
        )
        assert response.status_code == 404


# ── Medical data ─────────────────────────────────────────────────────────────


class TestMedicalData:
    """GET / PUT /api/v1/beneficiaries/{id}/medical"""

    async def test_get_medical_data_empty(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """Medical data for a beneficiary with none returns a default response."""
        response = await client.get(
            f"/api/v1/beneficiaries/{test_beneficiary.id}/medical",
            headers=msp_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["beneficiary_id"] == test_beneficiary.id

    async def test_update_and_get_medical_data(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """Write and then read back medical data."""
        payload = {
            "medication": "Paracetamol 500mg",
            "restrictions": "No heavy lifting",
            "allergies": "Pollen",
            "medical_notes": "Follow-up in 3 months",
        }
        put_resp = await client.put(
            f"/api/v1/beneficiaries/{test_beneficiary.id}/medical",
            headers=msp_headers,
            json=payload,
        )
        assert put_resp.status_code == 200
        put_data = put_resp.json()
        assert put_data["medication"] == "Paracetamol 500mg"
        assert put_data["allergies"] == "Pollen"

    async def test_medical_data_not_found(
        self, client: AsyncClient, msp_headers
    ):
        """Non-existent beneficiary returns 404."""
        response = await client.get(
            "/api/v1/beneficiaries/99999/medical",
            headers=msp_headers,
        )
        assert response.status_code == 404

    async def test_medical_data_access_denied_other_msp(
        self, client: AsyncClient, db_session, test_beneficiary, test_unit
    ):
        """MSP cannot access medical data for a beneficiary assigned to another MSP."""
        from app.models.user import User
        from app.utils.security import create_access_token, get_password_hash

        other_msp = User(
            email="other_msp@test.ch",
            hashed_password=get_password_hash("OtherMsp123!@#"),
            first_name="Other",
            last_name="MSP",
            role="MSP",
            unit_id=test_unit.id,
            is_active=True,
        )
        db_session.add(other_msp)
        await db_session.flush()
        await db_session.refresh(other_msp)

        token = create_access_token(data={"sub": str(other_msp.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get(
            f"/api/v1/beneficiaries/{test_beneficiary.id}/medical",
            headers=headers,
        )
        assert response.status_code == 403


# ── Contacts ─────────────────────────────────────────────────────────────────


class TestContacts:
    """CRUD for /api/v1/beneficiaries/{id}/contacts"""

    async def test_list_contacts_empty(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """Initially the contacts list is empty."""
        response = await client.get(
            f"/api/v1/beneficiaries/{test_beneficiary.id}/contacts",
            headers=msp_headers,
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_contact(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """Create an emergency contact."""
        response = await client.post(
            f"/api/v1/beneficiaries/{test_beneficiary.id}/contacts",
            headers=msp_headers,
            json={
                "contact_type": "emergency",
                "name": "Dr. Muller",
                "phone": "+41 21 555 66 77",
                "is_emergency_contact": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Dr. Muller"
        assert data["contact_type"] == "emergency"
        assert data["is_emergency_contact"] is True
        assert "id" in data

    async def test_update_contact(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Update an existing contact."""
        from app.models.beneficiary import Contact

        contact = Contact(
            beneficiary_id=test_beneficiary.id,
            contact_type="doctor",
            name="Dr. Original",
            phone="+41 00 000 00 00",
        )
        db_session.add(contact)
        await db_session.flush()
        await db_session.refresh(contact)

        response = await client.put(
            f"/api/v1/beneficiaries/{test_beneficiary.id}/contacts/{contact.id}",
            headers=msp_headers,
            json={"name": "Dr. Updated", "phone": "+41 21 999 88 77"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Dr. Updated"

    async def test_delete_contact(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Delete a contact returns 204."""
        from app.models.beneficiary import Contact

        contact = Contact(
            beneficiary_id=test_beneficiary.id,
            contact_type="other",
            name="To Delete",
        )
        db_session.add(contact)
        await db_session.flush()
        await db_session.refresh(contact)

        response = await client.delete(
            f"/api/v1/beneficiaries/{test_beneficiary.id}/contacts/{contact.id}",
            headers=msp_headers,
        )
        assert response.status_code == 204

    async def test_create_contact_beneficiary_not_found(
        self, client: AsyncClient, msp_headers
    ):
        """Creating a contact for a non-existent beneficiary returns 404."""
        response = await client.post(
            "/api/v1/beneficiaries/99999/contacts",
            headers=msp_headers,
            json={
                "contact_type": "emergency",
                "name": "Nobody",
            },
        )
        assert response.status_code == 404


# ── Risk behaviors ───────────────────────────────────────────────────────────


class TestRiskBehaviors:
    """CRUD for /api/v1/beneficiaries/{id}/risk-behaviors"""

    async def test_list_risk_behaviors_empty(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """Initially the risk-behaviors list is empty."""
        response = await client.get(
            f"/api/v1/beneficiaries/{test_beneficiary.id}/risk-behaviors",
            headers=msp_headers,
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_risk_behavior(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """Create a risk behavior record."""
        response = await client.post(
            f"/api/v1/beneficiaries/{test_beneficiary.id}/risk-behaviors",
            headers=msp_headers,
            json={
                "risk_type": "aggression",
                "description": "Verbal outbursts under stress",
                "severity": "medium",
                "preventive_measures": "De-escalation protocol",
                "reported_date": "2024-06-01",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["risk_type"] == "aggression"
        assert data["severity"] == "medium"
        assert data["is_active"] is True

    async def test_update_risk_behavior(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Update severity and deactivate a risk behavior."""
        from datetime import date

        from app.models.beneficiary import RiskBehavior

        risk = RiskBehavior(
            beneficiary_id=test_beneficiary.id,
            risk_type="self_harm",
            description="Original",
            severity="high",
            reported_date=date(2024, 5, 1),
            is_active=True,
        )
        db_session.add(risk)
        await db_session.flush()
        await db_session.refresh(risk)

        response = await client.put(
            f"/api/v1/beneficiaries/{test_beneficiary.id}/risk-behaviors/{risk.id}",
            headers=msp_headers,
            json={"severity": "low", "is_active": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["severity"] == "low"

    async def test_create_risk_behavior_beneficiary_not_found(
        self, client: AsyncClient, msp_headers
    ):
        """Creating a risk behavior for a non-existent beneficiary returns 404."""
        response = await client.post(
            "/api/v1/beneficiaries/99999/risk-behaviors",
            headers=msp_headers,
            json={
                "risk_type": "x",
                "description": "x",
                "severity": "low",
                "reported_date": "2024-01-01",
            },
        )
        assert response.status_code == 404
