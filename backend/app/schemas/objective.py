"""Objective-related schemas."""

from datetime import date, datetime
from typing import Literal

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
    achieved_at: datetime | None = None


# Actions
class ActionBase(BaseModel):
    """Base action schema."""

    description: str
    responsible: Literal["beneficiary", "msp", "other"] | None = None
    responsible_name: str | None = Field(None, max_length=100)
    due_date: date | None = None
    notes: str | None = None


class ActionCreate(ActionBase):
    """Schema for creating an action."""

    pass


class ActionUpdate(BaseModel):
    """Schema for updating an action."""

    description: str | None = None
    responsible: Literal["beneficiary", "msp", "other"] | None = None
    responsible_name: str | None = Field(None, max_length=100)
    due_date: date | None = None
    status: Literal["pending", "done"] | None = None
    notes: str | None = None


class ActionResponse(ActionBase):
    """Schema for action response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str


# Objectives
class ObjectiveBase(BaseModel):
    """Base objective schema."""

    title: str = Field(..., max_length=255)
    description: str | None = None
    objective_type: Literal["pai", "behavioral", "operational"]
    term: Literal["short", "medium", "long"]
    priority: Literal["high", "medium", "low"] = "medium"
    due_date: date | None = None
    reminder_frequency: Literal["daily", "weekly", "monthly", "none"] | None = None


class ObjectiveCreate(ObjectiveBase):
    """Schema for creating an objective."""

    pai_id: int | None = None
    beneficiary_id: int
    indicators: list[IndicatorCreate] | None = None
    actions: list[ActionCreate] | None = None


class ObjectiveUpdate(BaseModel):
    """Schema for updating an objective."""

    title: str | None = Field(None, max_length=255)
    description: str | None = None
    objective_type: Literal["pai", "behavioral", "operational"] | None = None
    term: Literal["short", "medium", "long"] | None = None
    priority: Literal["high", "medium", "low"] | None = None
    due_date: date | None = None
    reminder_frequency: Literal["daily", "weekly", "monthly", "none"] | None = None


class ObjectiveProgressUpdate(BaseModel):
    """Schema for updating objective progress."""

    progress: int = Field(..., ge=0, le=100)
    note: str | None = None


class ObjectiveStatusUpdate(BaseModel):
    """Schema for updating objective status."""

    status: Literal["pending", "in_progress", "achieved", "abandoned"]
    note: str | None = None


class ObjectiveResponse(ObjectiveBase):
    """Schema for objective response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pai_id: int | None = None
    beneficiary_id: int
    beneficiary_name: str | None = None
    status: str
    progress: int
    last_reminder_sent: datetime | None = None
    indicators: list[IndicatorResponse] | None = None
    actions: list[ActionResponse] | None = None
    created_at: datetime
    created_by_name: str | None = None


class ObjectiveOverview(BaseModel):
    """Schema for objective overview response."""

    id: int
    title: str
    status: str
    progress: int
    due_date: date | None = None
    is_overdue: bool = False


class BeneficiaryObjectives(BaseModel):
    """Objectives grouped by beneficiary."""

    beneficiary_id: int
    beneficiary_name: str
    unit_name: str | None = None
    objectives: list[ObjectiveOverview]


class ObjectivesOverviewResponse(BaseModel):
    """Schema for objectives overview response."""

    summary: dict
    by_beneficiary: list[BeneficiaryObjectives]
