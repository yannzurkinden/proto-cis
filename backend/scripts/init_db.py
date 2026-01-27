"""Database initialization script."""

import asyncio
import sys
sys.path.insert(0, ".")

from sqlalchemy import text

from app.database import engine, AsyncSessionLocal
from app.models.user import User
from app.models.unit import Unit
from app.models.journal import JournalCategory
from app.utils.security import get_password_hash


async def init_db():
    """Initialize database with default data."""
    async with AsyncSessionLocal() as session:
        # Create default units
        units = [
            Unit(name="Atelier Bois", description="Atelier de menuiserie"),
            Unit(name="Atelier Metal", description="Atelier de metallurgie"),
            Unit(name="Atelier Cuisine", description="Atelier de cuisine"),
            Unit(name="Atelier Jardinage", description="Atelier de jardinage"),
        ]

        for unit in units:
            session.add(unit)

        await session.flush()

        # Create admin user
        admin = User(
            email="admin@cis.local",
            hashed_password=get_password_hash("Admin123!@#$"),
            first_name="Admin",
            last_name="System",
            role="ADMIN",
            is_superuser=True,
        )
        session.add(admin)

        # Create journal categories
        categories = [
            JournalCategory(name="health", label="Sante", color="#10B981", icon="heart", sort_order=1),
            JournalCategory(name="behavior", label="Comportement", color="#F59E0B", icon="alert-triangle", sort_order=2),
            JournalCategory(name="conflict", label="Conflit", color="#EF4444", icon="zap", sort_order=3),
            JournalCategory(name="skills", label="Competences / Formation", color="#3B82F6", icon="book", sort_order=4),
            JournalCategory(name="private", label="Vie privee", color="#8B5CF6", icon="user", sort_order=5),
            JournalCategory(name="inter_unit", label="Echange inter-unites", color="#06B6D4", icon="users", sort_order=6),
            JournalCategory(name="interview", label="Entretien", color="#6366F1", icon="message-circle", sort_order=7),
            JournalCategory(name="incident", label="Incident", color="#DC2626", icon="alert-circle", sort_order=8),
            JournalCategory(name="progress", label="Progres / Reussite", color="#22C55E", icon="trending-up", sort_order=9),
            JournalCategory(name="other", label="Autre", color="#6B7280", icon="file-text", sort_order=10),
        ]

        for category in categories:
            session.add(category)

        await session.commit()

        print("Database initialized successfully!")
        print("Default admin user created: admin@cis.local / Admin123!@#$")


if __name__ == "__main__":
    asyncio.run(init_db())
