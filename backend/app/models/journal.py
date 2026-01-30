"""Journal entry models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.beneficiary import Beneficiary


class JournalCategory(Base):
    """Journal entry category."""

    __tablename__ = "journal_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # Hex color
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    entries: Mapped[list["JournalEntryCategory"]] = relationship(
        "JournalEntryCategory", back_populates="category"
    )


class JournalEntry(Base, TimestampMixin):
    """Journal entry model."""

    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[int] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    entry_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    visibility: Mapped[str] = mapped_column(
        String(20), default="unit", nullable=False
    )  # team, unit, inter_unit

    # Relationships
    beneficiary: Mapped["Beneficiary"] = relationship(
        "Beneficiary", back_populates="journal_entries"
    )
    categories: Mapped[list["JournalEntryCategory"]] = relationship(
        "JournalEntryCategory", back_populates="entry", cascade="all, delete-orphan"
    )
    tags: Mapped[list["JournalEntryTag"]] = relationship(
        "JournalEntryTag", back_populates="entry", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<JournalEntry(id={self.id}, title='{self.title}')>"


class JournalEntryCategory(Base):
    """Many-to-many association between journal entries and categories."""

    __tablename__ = "journal_entry_categories"

    journal_entry_id: Mapped[int] = mapped_column(
        ForeignKey("journal_entries.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("journal_categories.id"), primary_key=True, index=True
    )

    # Relationships
    entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="categories")
    category: Mapped["JournalCategory"] = relationship("JournalCategory", back_populates="entries")


class JournalEntryTag(Base):
    """Tags for journal entries."""

    __tablename__ = "journal_entry_tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    journal_entry_id: Mapped[int] = mapped_column(
        ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tag: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Relationships
    entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="tags")
