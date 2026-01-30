"""Unit schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UnitBase(BaseModel):
    """Base unit schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class UnitCreate(UnitBase):
    """Schema for creating a unit."""

    pass


class UnitUpdate(BaseModel):
    """Schema for updating a unit."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class UnitResponse(UnitBase):
    """Schema for unit response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
