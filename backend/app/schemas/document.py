"""Document schemas."""

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    """Base document schema."""

    document_type: Literal[
        "contract", "medical_cert", "evaluation", "report", "correspondence", "photo", "other"
    ]
    document_date: Optional[date] = None
    confidentiality: Literal["standard", "confidential", "highly_confidential"] = "standard"
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""

    beneficiary_id: Optional[int] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""

    document_type: Optional[
        Literal[
            "contract", "medical_cert", "evaluation", "report", "correspondence", "photo", "other"
        ]
    ] = None
    document_date: Optional[date] = None
    confidentiality: Optional[Literal["standard", "confidential", "highly_confidential"]] = None
    description: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Schema for document response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: Optional[int] = None
    original_filename: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    version: int
    is_current: bool
    uploaded_at: datetime
    uploaded_by: Optional[int] = None
