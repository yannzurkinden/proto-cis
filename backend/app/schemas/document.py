"""Document schemas."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    """Base document schema."""

    document_type: Literal[
        "contract", "medical_cert", "evaluation", "report", "correspondence", "photo", "other"
    ]
    document_date: date | None = None
    confidentiality: Literal["standard", "confidential", "highly_confidential"] = "standard"
    description: str | None = None


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""

    beneficiary_id: int | None = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""

    document_type: Literal["contract", "medical_cert", "evaluation", "report", "correspondence", "photo", "other"] | None = None
    document_date: date | None = None
    confidentiality: Literal["standard", "confidential", "highly_confidential"] | None = None
    description: str | None = None


class DocumentResponse(DocumentBase):
    """Schema for document response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: int | None = None
    original_filename: str
    file_size: int | None = None
    mime_type: str | None = None
    version: int
    is_current: bool
    uploaded_at: datetime
    uploaded_by: int | None = None
