"""Tests for beneficiary endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.beneficiary import Beneficiary


@pytest.fixture
async def test_beneficiary(db_session: AsyncSession, test_user):
    """Create a test beneficiary."""
    beneficiary = Beneficiary(
        first_name="Jean",
        last_name="Dupont",
        date_of_birth="1990-01-15",
        entry_date="2024-01-01",
        status="active",
        language="fr",
        referent_id=test_user.id,
        created_by=test_user.id,
    )
    db_session.add(beneficiary)
    await db_session.commit()
    await db_session.refresh(beneficiary)
    return beneficiary


@pytest.mark.asyncio
async def test_list_beneficiaries(client: AsyncClient, test_beneficiary, auth_headers):
    """Test listing beneficiaries."""
    response = await client.get("/api/v1/beneficiaries", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_beneficiary(client: AsyncClient, test_beneficiary, auth_headers):
    """Test getting a single beneficiary."""
    response = await client.get(
        f"/api/v1/beneficiaries/{test_beneficiary.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Jean"
    assert data["last_name"] == "Dupont"


@pytest.mark.asyncio
async def test_create_beneficiary(client: AsyncClient, auth_headers):
    """Test creating a beneficiary."""
    response = await client.post(
        "/api/v1/beneficiaries",
        headers=auth_headers,
        json={
            "first_name": "Marie",
            "last_name": "Martin",
            "date_of_birth": "1985-05-20",
            "entry_date": "2024-02-01",
            "language": "fr",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Marie"
    assert data["last_name"] == "Martin"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_update_beneficiary(client: AsyncClient, test_beneficiary, auth_headers):
    """Test updating a beneficiary."""
    response = await client.put(
        f"/api/v1/beneficiaries/{test_beneficiary.id}",
        headers=auth_headers,
        json={
            "phone": "+41 79 123 45 67",
            "city": "Lausanne",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "+41 79 123 45 67"
    assert data["city"] == "Lausanne"


@pytest.mark.asyncio
async def test_get_beneficiary_not_found(client: AsyncClient, auth_headers):
    """Test getting a non-existent beneficiary."""
    response = await client.get("/api/v1/beneficiaries/99999", headers=auth_headers)
    assert response.status_code == 404
