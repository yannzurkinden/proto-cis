"""PAI (Plan d'Accompagnement Individualis) schemas."""

from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict


class PAIBase(BaseModel):
    """Base PAI schema."""

    valid_from: date
    valid_to: Optional[date] = None
    strengths: Optional[str] = None
    difficulties: Optional[str] = None
    beneficiary_wishes: Optional[str] = None


class PAICreate(PAIBase):
    """Schema for creating a PAI."""

    pass


class PAIUpdate(BaseModel):
    """Schema for updating a PAI."""

    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    strengths: Optional[str] = None
    difficulties: Optional[str] = None
    beneficiary_wishes: Optional[str] = None
    status: Optional[Literal["draft", "active", "closed"]] = None


class ObjectiveSummary(BaseModel):
    """Summary of an objective for PAI response."""

    id: int
    title: str
    objective_type: str
    term: str
    status: str
    progress: int
    due_date: Optional[date] = None


class PAIResponse(PAIBase):
    """Schema for PAI response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: int
    status: str
    objectives: Optional[List[ObjectiveSummary]] = None
    created_at: datetime
    created_by: Optional[int] = None
    created_by_name: Optional[str] = None
