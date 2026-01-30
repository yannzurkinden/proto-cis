"""Skill and training schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# Skill reference schemas
class SkillCreate(BaseModel):
    """Schema for creating a skill."""

    name: str = Field(..., max_length=100)
    category: str | None = Field(None, max_length=50)
    description: str | None = None


class SkillUpdate(BaseModel):
    """Schema for updating a skill."""

    name: str | None = Field(None, max_length=100)
    category: str | None = Field(None, max_length=50)
    description: str | None = None
    is_active: bool | None = None


class SkillResponse(BaseModel):
    """Schema for skill response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str | None = None
    description: str | None = None
    is_active: bool = True
    sort_order: int = 0


# Beneficiary skill evaluation schemas
class BeneficiarySkillEvaluate(BaseModel):
    """Schema for evaluating a beneficiary's skill."""

    level: Literal["not_acquired", "in_progress", "acquired", "mastered"]
    comments: str | None = None


class BeneficiarySkillResponse(BaseModel):
    """Schema for beneficiary skill evaluation response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    skill_id: int
    skill_name: str | None = None
    level: str
    evaluation_date: date
    evaluated_by: int | None = None
    comments: str | None = None


# Training schemas
class TrainingCreate(BaseModel):
    """Schema for creating a training."""

    title: str = Field(..., max_length=255)
    training_date: date
    duration_hours: Decimal | None = None
    trainer: str | None = Field(None, max_length=200)
    comments: str | None = None


class TrainingUpdate(BaseModel):
    """Schema for updating a training."""

    title: str | None = Field(None, max_length=255)
    training_date: date | None = None
    duration_hours: Decimal | None = None
    trainer: str | None = Field(None, max_length=200)
    comments: str | None = None


class TrainingResponse(BaseModel):
    """Schema for training response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: int
    title: str
    training_date: date
    duration_hours: Decimal | None = None
    trainer: str | None = None
    comments: str | None = None
    created_at: datetime
