"""Document model for file management."""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.beneficiary import Beneficiary


class Document(Base):
    """Document model for file storage."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    beneficiary_id: Mapped[int | None] = mapped_column(
        ForeignKey("beneficiaries.id", ondelete="CASCADE"), nullable=True, index=True
    )

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    document_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # contract, medical_cert, evaluation, report, correspondence, other
    document_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    confidentiality: Mapped[str] = mapped_column(
        String(20), default="standard", nullable=False
    )  # standard, confidential, highly_confidential
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False, index=True
    )
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    previous_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id"), nullable=True
    )
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    beneficiary: Mapped[Optional["Beneficiary"]] = relationship(
        "Beneficiary", back_populates="documents"
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename='{self.original_filename}')>"
