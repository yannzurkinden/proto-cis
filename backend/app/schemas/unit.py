"""Unit schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UnitBase(BaseModel):
    """Base unit schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class UnitCreate(UnitBase):
    """Schema for creating a unit."""

    pass


class UnitUpdate(BaseModel):
    """Schema for updating a unit."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class UnitResponse(UnitBase):
    """Schema for unit response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
