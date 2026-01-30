"""Skill and training models."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.beneficiary import Beneficiary


class Skill(Base):
    """Skill reference model."""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class BeneficiarySkill(Base, TimestampMixin):
    """Skill evaluation for a beneficiary."""

    __tablename__ = "beneficiary_skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[int] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)

    level: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # not_acquired, in_progress, acquired, mastered
    evaluation_date: Mapped[date] = mapped_column(Date, nullable=False)
    evaluated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    beneficiary: Mapped["Beneficiary"] = relationship("Beneficiary", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill")


class Training(Base):
    """Training record for a beneficiary."""

    __tablename__ = "trainings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[int] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    training_date: Mapped[date] = mapped_column(Date, nullable=False)
    duration_hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    trainer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    certificate_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id"), nullable=True
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    # Relationships
    beneficiary: Mapped["Beneficiary"] = relationship("Beneficiary", back_populates="trainings")
