"""Journal entry schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class JournalCategoryResponse(BaseModel):
    """Schema for journal category response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    label: str
    color: str | None = None
    icon: str | None = None


class JournalEntryBase(BaseModel):
    """Base journal entry schema."""

    title: str = Field(..., max_length=255)
    content: str
    entry_date: datetime | None = None
    visibility: Literal["team", "unit", "inter_unit"] = "unit"


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a journal entry."""

    beneficiary_id: int
    category_ids: list[int] = []
    tags: list[str] = []


class JournalEntryUpdate(BaseModel):
    """Schema for updating a journal entry."""

    title: str | None = Field(None, max_length=255)
    content: str | None = None
    entry_date: datetime | None = None
    visibility: Literal["team", "unit", "inter_unit"] | None = None
    category_ids: list[int] | None = None
    tags: list[str] | None = None


class JournalEntryResponse(JournalEntryBase):
    """Schema for journal entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: int
    beneficiary_name: str | None = None
    author_id: int
    author_name: str | None = None
    categories: list[JournalCategoryResponse] = []
    tags: list[str] = []
    attachments_count: int = 0
    created_at: datetime
    updated_at: datetime
