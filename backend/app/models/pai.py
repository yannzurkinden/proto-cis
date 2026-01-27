"""PAI (Plan d'Accompagnement Individualis) model."""

from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.beneficiary import Beneficiary
    from app.models.objective import Objective
    from app.models.user import User


class PAI(Base, TimestampMixin):
    """Individualized Support Plan model."""

    __tablename__ = "pais"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[int] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(
        String(20), default="draft", nullable=False, index=True
    )  # draft, active, closed
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Initial assessment
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulties: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    beneficiary_wishes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Relationships
    beneficiary: Mapped["Beneficiary"] = relationship("Beneficiary", back_populates="pais")
    objectives: Mapped[List["Objective"]] = relationship(
        "Objective",
        back_populates="pai",
        cascade="all, delete-orphan",
        foreign_keys="Objective.pai_id",
    )

    def __repr__(self) -> str:
        return f"<PAI(id={self.id}, beneficiary_id={self.beneficiary_id}, status='{self.status}')>"
