"""Pytest configuration and fixtures for CIS backend tests."""

import datetime
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import *  # noqa: F403 - Import all models to register them with Base
from app.models.audit import Notification
from app.models.beneficiary import Beneficiary
from app.models.journal import JournalCategory
from app.models.unit import Unit
from app.models.user import User
from app.utils.security import create_access_token, get_password_hash

# ---------------------------------------------------------------------------
# Engine / session setup – in-memory SQLite shared via StaticPool
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine.sync_engine, "connect")
def _register_sqlite_functions(dbapi_connection, connection_record):
    """Register PostgreSQL-compatible functions so that models using
    ``server_default="now()"`` work under SQLite."""
    dbapi_connection.create_function(
        "now",
        0,
        lambda: datetime.datetime.now(datetime.UTC).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )


TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ---------------------------------------------------------------------------
# Database lifecycle – create / drop tables per test
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test and tear them down afterwards."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# Session & client fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session that is shared with the API client."""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with the database dependency overridden."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Unit fixture
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def test_unit(db_session: AsyncSession) -> Unit:
    """Create a test organisational unit."""
    unit = Unit(name="Atelier Test", description="Unit for testing", is_active=True)
    db_session.add(unit)
    await db_session.flush()
    await db_session.refresh(unit)
    return unit


@pytest_asyncio.fixture
async def second_unit(db_session: AsyncSession) -> Unit:
    """Create a second organisational unit."""
    unit = Unit(name="Atelier Secondaire", description="Second unit", is_active=True)
    db_session.add(unit)
    await db_session.flush()
    await db_session.refresh(unit)
    return unit


# ---------------------------------------------------------------------------
# User fixtures – various roles
# ---------------------------------------------------------------------------

_ADMIN_PASSWORD = "Admin123!@#abc"
_MSP_PASSWORD = "Msp12345!@#abc"
_RES_PASSWORD = "Res12345!@#abc"
_CONSULT_PASSWORD = "Consult123!@#"


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an ADMIN user."""
    user = User(
        email="admin@test.ch",
        hashed_password=get_password_hash(_ADMIN_PASSWORD),
        first_name="Admin",
        last_name="Test",
        role="ADMIN",
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_token(admin_user: User) -> str:
    return create_access_token(data={"sub": str(admin_user.id)})


@pytest_asyncio.fixture
async def admin_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
async def msp_user(db_session: AsyncSession, test_unit: Unit) -> User:
    """Create an MSP user assigned to *test_unit*."""
    user = User(
        email="msp@test.ch",
        hashed_password=get_password_hash(_MSP_PASSWORD),
        first_name="MSP",
        last_name="Test",
        role="MSP",
        unit_id=test_unit.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def msp_token(msp_user: User) -> str:
    return create_access_token(data={"sub": str(msp_user.id)})


@pytest_asyncio.fixture
async def msp_headers(msp_token: str) -> dict:
    return {"Authorization": f"Bearer {msp_token}"}


@pytest_asyncio.fixture
async def res_user(db_session: AsyncSession, test_unit: Unit) -> User:
    """Create a RES (management) user assigned to *test_unit*."""
    user = User(
        email="res@test.ch",
        hashed_password=get_password_hash(_RES_PASSWORD),
        first_name="RES",
        last_name="Test",
        role="RES",
        unit_id=test_unit.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def res_token(res_user: User) -> str:
    return create_access_token(data={"sub": str(res_user.id)})


@pytest_asyncio.fixture
async def res_headers(res_token: str) -> dict:
    return {"Authorization": f"Bearer {res_token}"}


@pytest_asyncio.fixture
async def consult_user(db_session: AsyncSession, test_unit: Unit) -> User:
    """Create a CONSULT user (read-only)."""
    user = User(
        email="consult@test.ch",
        hashed_password=get_password_hash(_CONSULT_PASSWORD),
        first_name="Consult",
        last_name="Test",
        role="CONSULT",
        unit_id=test_unit.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def consult_token(consult_user: User) -> str:
    return create_access_token(data={"sub": str(consult_user.id)})


@pytest_asyncio.fixture
async def consult_headers(consult_token: str) -> dict:
    return {"Authorization": f"Bearer {consult_token}"}


# ---------------------------------------------------------------------------
# Beneficiary fixture
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def test_beneficiary(
    db_session: AsyncSession, test_unit: Unit, msp_user: User
) -> Beneficiary:
    """Create a test beneficiary linked to *test_unit* and *msp_user*."""
    from datetime import date

    beneficiary = Beneficiary(
        first_name="Jean",
        last_name="Dupont",
        date_of_birth=date(1985, 3, 15),
        entry_date=date(2024, 1, 15),
        status="active",
        unit_id=test_unit.id,
        referent_id=msp_user.id,
        language="fr",
        created_by=msp_user.id,
    )
    db_session.add(beneficiary)
    await db_session.flush()
    await db_session.refresh(beneficiary)
    return beneficiary


@pytest_asyncio.fixture
async def second_beneficiary(
    db_session: AsyncSession, test_unit: Unit, msp_user: User
) -> Beneficiary:
    """Create a second test beneficiary."""
    from datetime import date

    beneficiary = Beneficiary(
        first_name="Marie",
        last_name="Martin",
        date_of_birth=date(1990, 7, 20),
        entry_date=date(2024, 3, 1),
        status="active",
        unit_id=test_unit.id,
        referent_id=msp_user.id,
        language="fr",
        created_by=msp_user.id,
    )
    db_session.add(beneficiary)
    await db_session.flush()
    await db_session.refresh(beneficiary)
    return beneficiary


# ---------------------------------------------------------------------------
# Journal category fixture
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def test_category(db_session: AsyncSession) -> JournalCategory:
    """Create a test journal category."""
    category = JournalCategory(
        name="observation",
        label="Observation",
        color="#4CAF50",
        icon="eye",
        is_active=True,
        sort_order=1,
    )
    db_session.add(category)
    await db_session.flush()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture
async def second_category(db_session: AsyncSession) -> JournalCategory:
    """Create a second journal category."""
    category = JournalCategory(
        name="incident",
        label="Incident",
        color="#F44336",
        icon="alert",
        is_active=True,
        sort_order=2,
    )
    db_session.add(category)
    await db_session.flush()
    await db_session.refresh(category)
    return category


# ---------------------------------------------------------------------------
# Notification fixture helpers
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def test_notifications(
    db_session: AsyncSession, msp_user: User
) -> list[Notification]:
    """Create several test notifications for *msp_user*."""
    now = datetime.datetime.now(datetime.UTC)
    notifications = []
    for i in range(5):
        n = Notification(
            user_id=msp_user.id,
            notification_type="info",
            title=f"Notification {i + 1}",
            message=f"Message body {i + 1}",
            is_read=(i < 2),  # first two are read
            read_at=now if i < 2 else None,
            created_at=now - datetime.timedelta(hours=i),
        )
        db_session.add(n)
        notifications.append(n)
    await db_session.flush()
    for n in notifications:
        await db_session.refresh(n)
    return notifications
