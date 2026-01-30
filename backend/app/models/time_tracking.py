"""Time tracking models for timeclock and absences."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.beneficiary import Beneficiary


class TimeEntry(Base, TimestampMixin):
    """Time entry for beneficiary work hours."""

    __tablename__ = "time_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[int] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False, index=True
    )

    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    time_in: Mapped[time | None] = mapped_column(Time, nullable=True)
    time_out: Mapped[time | None] = mapped_column(Time, nullable=True)
    entry_type: Mapped[str] = mapped_column(
        String(20), default="work", nullable=False
    )  # work, training, appointment
    hours_worked: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    beneficiary: Mapped["Beneficiary"] = relationship("Beneficiary", back_populates="time_entries")

    def calculate_hours(self) -> Decimal | None:
        """Calculate hours worked from time_in and time_out."""
        if self.time_in and self.time_out:
            time_in_dt = datetime.combine(date.today(), self.time_in)
            time_out_dt = datetime.combine(date.today(), self.time_out)
            diff = time_out_dt - time_in_dt
            return Decimal(str(diff.total_seconds() / 3600)).quantize(Decimal("0.01"))
        return None


class Absence(Base, TimestampMixin):
    """Absence record for a beneficiary."""

    __tablename__ = "absences"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[int] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False, index=True
    )

    absence_type: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )  # sick, vacation, accident, unauthorized, other
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    justification_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id"), nullable=True
    )
    validated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    beneficiary: Mapped["Beneficiary"] = relationship("Beneficiary", back_populates="absences")

    @property
    def duration_days(self) -> int:
        """Calculate duration in days."""
        return (self.end_date - self.start_date).days + 1


class VacationBalance(Base):
    """Vacation balance for a beneficiary."""

    __tablename__ = "vacation_balances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[int] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False, index=True
    )

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    entitled_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    taken_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    beneficiary: Mapped["Beneficiary"] = relationship(
        "Beneficiary", back_populates="vacation_balances"
    )

    @property
    def remaining_days(self) -> Decimal:
        """Calculate remaining vacation days."""
        return self.entitled_days - self.taken_days
