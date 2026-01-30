"""Beneficiary models including medical data, contacts, and risk behaviors."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.journal import JournalEntry
    from app.models.objective import Objective
    from app.models.pai import PAI
    from app.models.skill import BeneficiarySkill, Training
    from app.models.time_tracking import Absence, TimeEntry, VacationBalance
    from app.models.unit import Unit
    from app.models.user import User


class Beneficiary(Base, TimestampMixin):
    """Beneficiary (CAI) model."""

    __tablename__ = "beneficiaries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Personal data
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="fr", nullable=False)

    # Administrative data
    ai_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pension_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # quarter, half, three_quarter, full
    guardianship_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    guardian_contact_id: Mapped[int | None] = mapped_column(
        ForeignKey("contacts.id", use_alter=True), nullable=True
    )
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    exit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="active", nullable=False, index=True
    )  # active, paused, exited

    # Contract data
    contract_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    occupation_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    salary: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("units.id"), nullable=True, index=True
    )
    referent_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Relationships
    unit: Mapped[Optional["Unit"]] = relationship("Unit", back_populates="beneficiaries")
    referent: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="beneficiaries",
        foreign_keys=[referent_id],
    )
    medical_data: Mapped[Optional["BeneficiaryMedicalData"]] = relationship(
        "BeneficiaryMedicalData",
        back_populates="beneficiary",
        uselist=False,
        cascade="all, delete-orphan",
    )
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        back_populates="beneficiary",
        cascade="all, delete-orphan",
        foreign_keys="Contact.beneficiary_id",
    )
    risk_behaviors: Mapped[list["RiskBehavior"]] = relationship(
        "RiskBehavior", back_populates="beneficiary", cascade="all, delete-orphan"
    )
    pais: Mapped[list["PAI"]] = relationship(
        "PAI", back_populates="beneficiary", cascade="all, delete-orphan"
    )
    objectives: Mapped[list["Objective"]] = relationship(
        "Objective", back_populates="beneficiary", cascade="all, delete-orphan"
    )
    journal_entries: Mapped[list["JournalEntry"]] = relationship(
        "JournalEntry", back_populates="beneficiary", cascade="all, delete-orphan"
    )
    time_entries: Mapped[list["TimeEntry"]] = relationship(
        "TimeEntry", back_populates="beneficiary", cascade="all, delete-orphan"
    )
    absences: Mapped[list["Absence"]] = relationship(
        "Absence", back_populates="beneficiary", cascade="all, delete-orphan"
    )
    vacation_balances: Mapped[list["VacationBalance"]] = relationship(
        "VacationBalance", back_populates="beneficiary", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="beneficiary", cascade="all, delete-orphan"
    )
    skills: Mapped[list["BeneficiarySkill"]] = relationship(
        "BeneficiarySkill", back_populates="beneficiary", cascade="all, delete-orphan"
    )
    trainings: Mapped[list["Training"]] = relationship(
        "Training", back_populates="beneficiary", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        """Return beneficiary's full name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Beneficiary(id={self.id}, name='{self.full_name}')>"


class BeneficiaryMedicalData(Base):
    """Medical data for a beneficiary (encrypted)."""

    __tablename__ = "beneficiary_medical_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[int] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Encrypted medical data
    medication: Mapped[str | None] = mapped_column(Text, nullable=True)
    restrictions: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    medical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        onupdate="now()",
        nullable=False,
    )
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Relationships
    beneficiary: Mapped["Beneficiary"] = relationship(
        "Beneficiary", back_populates="medical_data"
    )


class Contact(Base, TimestampMixin):
    """Contact network for a beneficiary."""

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[int | None] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=True, index=True
    )

    contact_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # emergency, doctor, psychologist, ai_referent, other
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    organization: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_emergency_contact: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    beneficiary: Mapped[Optional["Beneficiary"]] = relationship(
        "Beneficiary",
        back_populates="contacts",
        foreign_keys=[beneficiary_id],
    )


class RiskBehavior(Base, TimestampMixin):
    """Risk behaviors for a beneficiary."""

    __tablename__ = "risk_behaviors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[int] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False, index=True
    )

    risk_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # low, medium, high, critical
    preventive_measures: Mapped[str | None] = mapped_column(Text, nullable=True)
    reported_date: Mapped[date] = mapped_column(Date, nullable=False)
    reported_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    beneficiary: Mapped["Beneficiary"] = relationship(
        "Beneficiary", back_populates="risk_behaviors"
    )
