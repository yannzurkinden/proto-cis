"""Objective, ObjectiveIndicator, and Action models."""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.beneficiary import Beneficiary
    from app.models.pai import PAI


class Objective(Base, TimestampMixin):
    """Objective model."""

    __tablename__ = "objectives"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pai_id: Mapped[int | None] = mapped_column(
        ForeignKey("pais.id", ondelete="CASCADE"), nullable=True, index=True
    )
    beneficiary_id: Mapped[int] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    objective_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # pai, behavioral, operational
    term: Mapped[str] = mapped_column(String(20), nullable=False)  # short, medium, long
    priority: Mapped[str] = mapped_column(
        String(10), default="medium", nullable=False
    )  # high, medium, low
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True
    )  # pending, in_progress, achieved, abandoned
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    # Reminders
    reminder_frequency: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # daily, weekly, monthly, none
    last_reminder_sent: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Relationships
    pai: Mapped[Optional["PAI"]] = relationship(
        "PAI", back_populates="objectives", foreign_keys=[pai_id]
    )
    beneficiary: Mapped["Beneficiary"] = relationship("Beneficiary", back_populates="objectives")
    indicators: Mapped[list["ObjectiveIndicator"]] = relationship(
        "ObjectiveIndicator", back_populates="objective", cascade="all, delete-orphan"
    )
    actions: Mapped[list["Action"]] = relationship(
        "Action", back_populates="objective", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Objective(id={self.id}, title='{self.title}', status='{self.status}')>"


class ObjectiveIndicator(Base):
    """Success indicator for an objective."""

    __tablename__ = "objective_indicators"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    objective_id: Mapped[int] = mapped_column(
        ForeignKey("objectives.id", ondelete="CASCADE"), nullable=False, index=True
    )

    description: Mapped[str] = mapped_column(String(255), nullable=False)
    is_achieved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    achieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    objective: Mapped["Objective"] = relationship("Objective", back_populates="indicators")


class Action(Base, TimestampMixin):
    """Action/task to achieve an objective."""

    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    objective_id: Mapped[int] = mapped_column(
        ForeignKey("objectives.id", ondelete="CASCADE"), nullable=False, index=True
    )

    description: Mapped[str] = mapped_column(Text, nullable=False)
    responsible: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # beneficiary, msp, other
    responsible_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True
    )  # pending, done
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    objective: Mapped["Objective"] = relationship("Objective", back_populates="actions")
