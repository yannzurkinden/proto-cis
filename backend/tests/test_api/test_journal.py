"""Tests for journal entry endpoints (/api/v1/journal/*)."""

from httpx import AsyncClient

# ── Create journal entry ─────────────────────────────────────────────────────


class TestCreateJournalEntry:
    """POST /api/v1/journal"""

    async def test_create_journal_entry(
        self, client: AsyncClient, msp_headers, test_beneficiary
    ):
        """MSP can create a journal entry."""
        response = await client.post(
            "/api/v1/journal",
            headers=msp_headers,
            json={
                "beneficiary_id": test_beneficiary.id,
                "title": "Observation du jour",
                "content": "Le beneficiaire a montre une bonne motivation.",
                "visibility": "unit",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Observation du jour"
        assert data["beneficiary_id"] == test_beneficiary.id
        assert "id" in data
        assert "created_at" in data

    async def test_create_journal_entry_with_category(
        self,
        client: AsyncClient,
        msp_headers,
        test_beneficiary,
        test_category,
    ):
        """Create a journal entry linked to a category."""
        response = await client.post(
            "/api/v1/journal",
            headers=msp_headers,
            json={
                "beneficiary_id": test_beneficiary.id,
                "title": "Observation categorisee",
                "content": "Content with category.",
                "category_ids": [test_category.id],
                "tags": ["motivation", "progress"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data.get("tags", [])) == 2
        # categories may or may not be included in response depending on load
        assert "motivation" in data["tags"]

    async def test_create_journal_entry_beneficiary_not_found(
        self, client: AsyncClient, msp_headers
    ):
        """Non-existent beneficiary returns 404."""
        response = await client.post(
            "/api/v1/journal",
            headers=msp_headers,
            json={
                "beneficiary_id": 99999,
                "title": "Nope",
                "content": "Content",
            },
        )
        assert response.status_code == 404

    async def test_create_journal_entry_missing_fields(
        self, client: AsyncClient, msp_headers
    ):
        """Missing required fields returns 422."""
        response = await client.post(
            "/api/v1/journal",
            headers=msp_headers,
            json={"title": "Incomplete"},
        )
        assert response.status_code == 422

    async def test_create_journal_entry_consult_forbidden(
        self, client: AsyncClient, consult_headers, test_beneficiary
    ):
        """CONSULT role cannot create journal entries."""
        response = await client.post(
            "/api/v1/journal",
            headers=consult_headers,
            json={
                "beneficiary_id": test_beneficiary.id,
                "title": "Not allowed",
                "content": "Content",
            },
        )
        assert response.status_code == 403


# ── List journal entries ─────────────────────────────────────────────────────


class TestListJournalEntries:
    """GET /api/v1/journal"""

    async def test_list_journal_entries(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """List journal entries returns paginated results."""
        import datetime

        from app.models.journal import JournalEntry

        entry = JournalEntry(
            beneficiary_id=test_beneficiary.id,
            author_id=(await _get_msp_id(db_session)),
            title="Listed entry",
            content="Some content",
            entry_date=datetime.datetime.now(datetime.UTC),
        )
        db_session.add(entry)
        await db_session.flush()

        response = await client.get("/api/v1/journal", headers=msp_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_list_journal_entries_filter_by_beneficiary(
        self, client: AsyncClient, admin_headers, test_beneficiary, db_session
    ):
        """Filter journal entries by beneficiary_id."""
        import datetime

        from sqlalchemy import select

        from app.models.journal import JournalEntry
        from app.models.user import User

        # Use admin as author
        result = await db_session.execute(
            select(User).where(User.email == "admin@test.ch")
        )
        admin = result.scalar_one()

        entry = JournalEntry(
            beneficiary_id=test_beneficiary.id,
            author_id=admin.id,
            title="Filtered entry",
            content="Content",
            entry_date=datetime.datetime.now(datetime.UTC),
        )
        db_session.add(entry)
        await db_session.flush()

        response = await client.get(
            f"/api/v1/journal?beneficiary_id={test_beneficiary.id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1


# ── Get journal entry ────────────────────────────────────────────────────────


class TestGetJournalEntry:
    """GET /api/v1/journal/{id}"""

    async def test_get_journal_entry(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Fetch a journal entry by ID."""
        import datetime

        from app.models.journal import JournalEntry

        entry = JournalEntry(
            beneficiary_id=test_beneficiary.id,
            author_id=(await _get_msp_id(db_session)),
            title="Get me",
            content="Detailed content",
            entry_date=datetime.datetime.now(datetime.UTC),
        )
        db_session.add(entry)
        await db_session.flush()
        await db_session.refresh(entry)

        response = await client.get(
            f"/api/v1/journal/{entry.id}", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entry.id
        assert data["title"] == "Get me"

    async def test_get_journal_entry_not_found(
        self, client: AsyncClient, msp_headers
    ):
        response = await client.get("/api/v1/journal/99999", headers=msp_headers)
        assert response.status_code == 404


# ── Update journal entry ─────────────────────────────────────────────────────


class TestUpdateJournalEntry:
    """PUT /api/v1/journal/{id}"""

    async def test_update_journal_entry_by_author(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Author can update their own entry."""
        import datetime

        from app.models.journal import JournalEntry

        msp_id = await _get_msp_id(db_session)
        entry = JournalEntry(
            beneficiary_id=test_beneficiary.id,
            author_id=msp_id,
            title="Original",
            content="Original content",
            entry_date=datetime.datetime.now(datetime.UTC),
        )
        db_session.add(entry)
        await db_session.flush()
        await db_session.refresh(entry)

        response = await client.put(
            f"/api/v1/journal/{entry.id}",
            headers=msp_headers,
            json={"title": "Updated title", "content": "Updated content"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"

    async def test_update_journal_entry_by_admin(
        self,
        client: AsyncClient,
        admin_headers,
        test_beneficiary,
        db_session,
        msp_user,
    ):
        """ADMIN can update entries created by other users."""
        import datetime

        from app.models.journal import JournalEntry

        entry = JournalEntry(
            beneficiary_id=test_beneficiary.id,
            author_id=msp_user.id,
            title="MSP entry",
            content="Content",
            entry_date=datetime.datetime.now(datetime.UTC),
        )
        db_session.add(entry)
        await db_session.flush()
        await db_session.refresh(entry)

        response = await client.put(
            f"/api/v1/journal/{entry.id}",
            headers=admin_headers,
            json={"title": "Admin edited"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Admin edited"

    async def test_update_journal_entry_by_non_author_forbidden(
        self, client: AsyncClient, test_beneficiary, db_session, test_unit
    ):
        """Non-author MSP cannot update another's entry."""
        import datetime

        from app.models.journal import JournalEntry
        from app.models.user import User
        from app.utils.security import create_access_token, get_password_hash

        # Create the entry with the regular MSP
        msp_id = await _get_msp_id(db_session)
        entry = JournalEntry(
            beneficiary_id=test_beneficiary.id,
            author_id=msp_id,
            title="Owned by MSP",
            content="Content",
            entry_date=datetime.datetime.now(datetime.UTC),
        )
        db_session.add(entry)
        await db_session.flush()
        await db_session.refresh(entry)

        # Create another MSP
        other = User(
            email="msp_other@test.ch",
            hashed_password=get_password_hash("OtherMsp123!@#"),
            first_name="Other",
            last_name="MSP",
            role="MSP",
            unit_id=test_unit.id,
            is_active=True,
        )
        db_session.add(other)
        await db_session.flush()
        await db_session.refresh(other)

        token = create_access_token(data={"sub": str(other.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.put(
            f"/api/v1/journal/{entry.id}",
            headers=headers,
            json={"title": "Hijacked"},
        )
        assert response.status_code == 403

    async def test_update_journal_entry_not_found(
        self, client: AsyncClient, msp_headers
    ):
        response = await client.put(
            "/api/v1/journal/99999",
            headers=msp_headers,
            json={"title": "x"},
        )
        assert response.status_code == 404


# ── Delete journal entry ─────────────────────────────────────────────────────


class TestDeleteJournalEntry:
    """DELETE /api/v1/journal/{id}"""

    async def test_delete_by_author(
        self, client: AsyncClient, msp_headers, test_beneficiary, db_session
    ):
        """Author can delete their own entry."""
        import datetime

        from app.models.journal import JournalEntry

        msp_id = await _get_msp_id(db_session)
        entry = JournalEntry(
            beneficiary_id=test_beneficiary.id,
            author_id=msp_id,
            title="To delete",
            content="Content",
            entry_date=datetime.datetime.now(datetime.UTC),
        )
        db_session.add(entry)
        await db_session.flush()
        await db_session.refresh(entry)

        response = await client.delete(
            f"/api/v1/journal/{entry.id}", headers=msp_headers
        )
        assert response.status_code == 204

    async def test_delete_by_admin(
        self,
        client: AsyncClient,
        admin_headers,
        test_beneficiary,
        db_session,
        msp_user,
    ):
        """ADMIN can delete any entry."""
        import datetime

        from app.models.journal import JournalEntry

        entry = JournalEntry(
            beneficiary_id=test_beneficiary.id,
            author_id=msp_user.id,
            title="Admin delete",
            content="Content",
            entry_date=datetime.datetime.now(datetime.UTC),
        )
        db_session.add(entry)
        await db_session.flush()
        await db_session.refresh(entry)

        response = await client.delete(
            f"/api/v1/journal/{entry.id}", headers=admin_headers
        )
        assert response.status_code == 204

    async def test_delete_by_non_author_forbidden(
        self, client: AsyncClient, test_beneficiary, db_session, test_unit
    ):
        """Non-author MSP cannot delete another's entry."""
        import datetime

        from app.models.journal import JournalEntry
        from app.models.user import User
        from app.utils.security import create_access_token, get_password_hash

        msp_id = await _get_msp_id(db_session)
        entry = JournalEntry(
            beneficiary_id=test_beneficiary.id,
            author_id=msp_id,
            title="Protected",
            content="Content",
            entry_date=datetime.datetime.now(datetime.UTC),
        )
        db_session.add(entry)
        await db_session.flush()
        await db_session.refresh(entry)

        other = User(
            email="msp_del@test.ch",
            hashed_password=get_password_hash("OtherDel123!@#x"),
            first_name="Other",
            last_name="Del",
            role="MSP",
            unit_id=test_unit.id,
            is_active=True,
        )
        db_session.add(other)
        await db_session.flush()
        await db_session.refresh(other)

        token = create_access_token(data={"sub": str(other.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.delete(
            f"/api/v1/journal/{entry.id}", headers=headers
        )
        assert response.status_code == 403

    async def test_delete_not_found(
        self, client: AsyncClient, msp_headers
    ):
        response = await client.delete("/api/v1/journal/99999", headers=msp_headers)
        assert response.status_code == 404


# ── Categories ───────────────────────────────────────────────────────────────


class TestListCategories:
    """GET /api/v1/journal/categories"""

    async def test_list_categories(
        self, client: AsyncClient, msp_headers, test_category
    ):
        """List all active journal categories."""
        response = await client.get(
            "/api/v1/journal/categories", headers=msp_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == "observation"

    async def test_list_categories_unauthenticated(self, client: AsyncClient):
        """Unauthenticated returns 403."""
        response = await client.get("/api/v1/journal/categories")
        assert response.status_code == 403


# ── Helper ───────────────────────────────────────────────────────────────────


async def _get_msp_id(db_session) -> int:
    """Retrieve the MSP user's ID from the session."""
    from sqlalchemy import select

    from app.models.user import User

    result = await db_session.execute(
        select(User).where(User.email == "msp@test.ch")
    )
    user = result.scalar_one()
    return user.id
