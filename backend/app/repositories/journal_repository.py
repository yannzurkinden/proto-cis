"""Journal repository for database operations."""

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.journal import (
    JournalEntry,
    JournalCategory,
    JournalEntryCategory,
    JournalEntryTag,
)
from app.models.beneficiary import Beneficiary
from app.repositories.base import BaseRepository


class JournalRepository(BaseRepository[JournalEntry]):
    """Repository for JournalEntry model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, JournalEntry)

    async def get_by_id_with_relations(self, id: int) -> Optional[JournalEntry]:
        """Get journal entry by ID with all relations loaded."""
        result = await self.db.execute(
            select(JournalEntry)
            .options(
                selectinload(JournalEntry.categories).selectinload(JournalEntryCategory.category),
                selectinload(JournalEntry.tags),
                selectinload(JournalEntry.beneficiary),
            )
            .where(JournalEntry.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all_filtered(
        self,
        skip: int = 0,
        limit: int = 20,
        beneficiary_id: Optional[int] = None,
        author_id: Optional[int] = None,
        category_ids: Optional[List[int]] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        unit_id: Optional[int] = None,
    ) -> tuple[List[JournalEntry], int]:
        """Get all journal entries with filtering and pagination."""
        query = (
            select(JournalEntry)
            .options(
                selectinload(JournalEntry.categories).selectinload(JournalEntryCategory.category),
                selectinload(JournalEntry.tags),
                selectinload(JournalEntry.beneficiary),
            )
        )

        # Apply filters
        if beneficiary_id:
            query = query.where(JournalEntry.beneficiary_id == beneficiary_id)
        if author_id:
            query = query.where(JournalEntry.author_id == author_id)
        if date_from:
            query = query.where(JournalEntry.entry_date >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            query = query.where(JournalEntry.entry_date <= datetime.combine(date_to, datetime.max.time()))
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    JournalEntry.title.ilike(search_pattern),
                    JournalEntry.content.ilike(search_pattern),
                )
            )
        if unit_id:
            query = query.join(Beneficiary).where(Beneficiary.unit_id == unit_id)

        # Filter by categories
        if category_ids:
            query = query.join(JournalEntryCategory).where(
                JournalEntryCategory.category_id.in_(category_ids)
            )

        # Filter by tags
        if tags:
            query = query.join(JournalEntryTag).where(JournalEntryTag.tag.in_(tags))

        # Count query
        count_query = select(func.count(func.distinct(JournalEntry.id))).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginated query
        query = (
            query.distinct()
            .offset(skip)
            .limit(limit)
            .order_by(JournalEntry.entry_date.desc())
        )
        result = await self.db.execute(query)
        entries = list(result.scalars().all())

        return entries, total

    async def create_entry(
        self,
        data: dict,
        author_id: int,
        category_ids: List[int],
        tags: List[str],
    ) -> JournalEntry:
        """Create a new journal entry with categories and tags."""
        entry = JournalEntry(author_id=author_id, **data)
        self.db.add(entry)
        await self.db.flush()

        # Add categories
        for category_id in category_ids:
            entry_category = JournalEntryCategory(
                journal_entry_id=entry.id,
                category_id=category_id,
            )
            self.db.add(entry_category)

        # Add tags
        for tag in tags:
            entry_tag = JournalEntryTag(
                journal_entry_id=entry.id,
                tag=tag,
            )
            self.db.add(entry_tag)

        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def update_entry(
        self,
        entry: JournalEntry,
        data: dict,
        category_ids: Optional[List[int]] = None,
        tags: Optional[List[str]] = None,
    ) -> JournalEntry:
        """Update a journal entry."""
        for key, value in data.items():
            if hasattr(entry, key) and value is not None:
                setattr(entry, key, value)

        # Update categories if provided
        if category_ids is not None:
            # Remove existing categories
            await self.db.execute(
                JournalEntryCategory.__table__.delete().where(
                    JournalEntryCategory.journal_entry_id == entry.id
                )
            )
            # Add new categories
            for category_id in category_ids:
                entry_category = JournalEntryCategory(
                    journal_entry_id=entry.id,
                    category_id=category_id,
                )
                self.db.add(entry_category)

        # Update tags if provided
        if tags is not None:
            # Remove existing tags
            await self.db.execute(
                JournalEntryTag.__table__.delete().where(
                    JournalEntryTag.journal_entry_id == entry.id
                )
            )
            # Add new tags
            for tag in tags:
                entry_tag = JournalEntryTag(
                    journal_entry_id=entry.id,
                    tag=tag,
                )
                self.db.add(entry_tag)

        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    # Category operations
    async def get_all_categories(self, active_only: bool = True) -> List[JournalCategory]:
        """Get all journal categories."""
        query = select(JournalCategory)

        if active_only:
            query = query.where(JournalCategory.is_active == True)

        query = query.order_by(JournalCategory.sort_order)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_tags_for_beneficiary(self, beneficiary_id: int) -> List[str]:
        """Get all unique tags used for a beneficiary's journal entries."""
        result = await self.db.execute(
            select(func.distinct(JournalEntryTag.tag))
            .join(JournalEntry)
            .where(JournalEntry.beneficiary_id == beneficiary_id)
            .order_by(JournalEntryTag.tag)
        )
        return [row[0] for row in result.all()]

    async def get_recent_entries(
        self,
        beneficiary_id: Optional[int] = None,
        unit_id: Optional[int] = None,
        limit: int = 10,
    ) -> List[JournalEntry]:
        """Get recent journal entries."""
        query = (
            select(JournalEntry)
            .options(
                selectinload(JournalEntry.categories).selectinload(JournalEntryCategory.category),
                selectinload(JournalEntry.beneficiary),
            )
        )

        if beneficiary_id:
            query = query.where(JournalEntry.beneficiary_id == beneficiary_id)
        if unit_id:
            query = query.join(Beneficiary).where(Beneficiary.unit_id == unit_id)

        query = query.order_by(JournalEntry.entry_date.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
