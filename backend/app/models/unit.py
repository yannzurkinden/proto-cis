"""Unit model for organizational units/workshops."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.beneficiary import Beneficiary
    from app.models.user import User


class Unit(Base, TimestampMixin):
    """Unit/Workshop model."""

    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="unit")
    beneficiaries: Mapped[list["Beneficiary"]] = relationship(
        "Beneficiary", back_populates="unit"
    )

    def __repr__(self) -> str:
        return f"<Unit(id={self.id}, name='{self.name}')>"
