"""Journal entry schemas."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class JournalCategoryResponse(BaseModel):
    """Schema for journal category response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    label: str
    color: Optional[str] = None
    icon: Optional[str] = None


class JournalEntryBase(BaseModel):
    """Base journal entry schema."""

    title: str = Field(..., max_length=255)
    content: str
    entry_date: Optional[datetime] = None
    visibility: Literal["team", "unit", "inter_unit"] = "unit"


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a journal entry."""

    beneficiary_id: int
    category_ids: List[int] = []
    tags: List[str] = []


class JournalEntryUpdate(BaseModel):
    """Schema for updating a journal entry."""

    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    entry_date: Optional[datetime] = None
    visibility: Optional[Literal["team", "unit", "inter_unit"]] = None
    category_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None


class JournalEntryResponse(JournalEntryBase):
    """Schema for journal entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: int
    beneficiary_name: Optional[str] = None
    author_id: int
    author_name: Optional[str] = None
    categories: List[JournalCategoryResponse] = []
    tags: List[str] = []
    attachments_count: int = 0
    created_at: datetime
    updated_at: datetime
