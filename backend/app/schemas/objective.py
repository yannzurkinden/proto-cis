"""Objective-related schemas."""

from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# Indicators
class IndicatorBase(BaseModel):
    """Base indicator schema."""

    description: str = Field(..., max_length=255)


class IndicatorCreate(IndicatorBase):
    """Schema for creating an indicator."""

    pass


class IndicatorResponse(IndicatorBase):
    """Schema for indicator response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_achieved: bool
    achieved_at: Optional[datetime] = None


# Actions
class ActionBase(BaseModel):
    """Base action schema."""

    description: str
    responsible: Optional[Literal["beneficiary", "msp", "other"]] = None
    responsible_name: Optional[str] = Field(None, max_length=100)
    due_date: Optional[date] = None
    notes: Optional[str] = None


class ActionCreate(ActionBase):
    """Schema for creating an action."""

    pass


class ActionUpdate(BaseModel):
    """Schema for updating an action."""

    description: Optional[str] = None
    responsible: Optional[Literal["beneficiary", "msp", "other"]] = None
    responsible_name: Optional[str] = Field(None, max_length=100)
    due_date: Optional[date] = None
    status: Optional[Literal["pending", "done"]] = None
    notes: Optional[str] = None


class ActionResponse(ActionBase):
    """Schema for action response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str


# Objectives
class ObjectiveBase(BaseModel):
    """Base objective schema."""

    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    objective_type: Literal["pai", "behavioral", "operational"]
    term: Literal["short", "medium", "long"]
    priority: Literal["high", "medium", "low"] = "medium"
    due_date: Optional[date] = None
    reminder_frequency: Optional[Literal["daily", "weekly", "monthly", "none"]] = None


class ObjectiveCreate(ObjectiveBase):
    """Schema for creating an objective."""

    pai_id: Optional[int] = None
    beneficiary_id: int
    indicators: Optional[List[IndicatorCreate]] = None
    actions: Optional[List[ActionCreate]] = None


class ObjectiveUpdate(BaseModel):
    """Schema for updating an objective."""

    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    objective_type: Optional[Literal["pai", "behavioral", "operational"]] = None
    term: Optional[Literal["short", "medium", "long"]] = None
    priority: Optional[Literal["high", "medium", "low"]] = None
    due_date: Optional[date] = None
    reminder_frequency: Optional[Literal["daily", "weekly", "monthly", "none"]] = None


class ObjectiveProgressUpdate(BaseModel):
    """Schema for updating objective progress."""

    progress: int = Field(..., ge=0, le=100)
    note: Optional[str] = None


class ObjectiveStatusUpdate(BaseModel):
    """Schema for updating objective status."""

    status: Literal["pending", "in_progress", "achieved", "abandoned"]
    note: Optional[str] = None


class ObjectiveResponse(ObjectiveBase):
    """Schema for objective response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pai_id: Optional[int] = None
    beneficiary_id: int
    beneficiary_name: Optional[str] = None
    status: str
    progress: int
    last_reminder_sent: Optional[datetime] = None
    indicators: Optional[List[IndicatorResponse]] = None
    actions: Optional[List[ActionResponse]] = None
    created_at: datetime
    created_by_name: Optional[str] = None


class ObjectiveOverview(BaseModel):
    """Schema for objective overview response."""

    id: int
    title: str
    status: str
    progress: int
    due_date: Optional[date] = None
    is_overdue: bool = False


class BeneficiaryObjectives(BaseModel):
    """Objectives grouped by beneficiary."""

    beneficiary_id: int
    beneficiary_name: str
    unit_name: Optional[str] = None
    objectives: List[ObjectiveOverview]


class ObjectivesOverviewResponse(BaseModel):
    """Schema for objectives overview response."""

    summary: dict
    by_beneficiary: List[BeneficiaryObjectives]
