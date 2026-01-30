"""PAI (Plan d'Accompagnement Individualis) schemas."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class PAIBase(BaseModel):
    """Base PAI schema."""

    valid_from: date
    valid_to: date | None = None
    strengths: str | None = None
    difficulties: str | None = None
    beneficiary_wishes: str | None = None


class PAICreate(PAIBase):
    """Schema for creating a PAI."""

    pass


class PAIUpdate(BaseModel):
    """Schema for updating a PAI."""

    valid_from: date | None = None
    valid_to: date | None = None
    strengths: str | None = None
    difficulties: str | None = None
    beneficiary_wishes: str | None = None
    status: Literal["draft", "active", "closed"] | None = None


class ObjectiveSummary(BaseModel):
    """Summary of an objective for PAI response."""

    id: int
    title: str
    objective_type: str
    term: str
    status: str
    progress: int
    due_date: date | None = None


class PAIResponse(PAIBase):
    """Schema for PAI response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: int
    status: str
    objectives: list[ObjectiveSummary] | None = None
    created_at: datetime
    created_by: int | None = None
    created_by_name: str | None = None
