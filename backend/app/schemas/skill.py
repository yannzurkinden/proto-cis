"""Skill and training schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# Skill reference schemas
class SkillCreate(BaseModel):
    """Schema for creating a skill."""

    name: str = Field(..., max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class SkillUpdate(BaseModel):
    """Schema for updating a skill."""

    name: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SkillResponse(BaseModel):
    """Schema for skill response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


# Beneficiary skill evaluation schemas
class BeneficiarySkillEvaluate(BaseModel):
    """Schema for evaluating a beneficiary's skill."""

    level: Literal["not_acquired", "in_progress", "acquired", "mastered"]
    comments: Optional[str] = None


class BeneficiarySkillResponse(BaseModel):
    """Schema for beneficiary skill evaluation response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    skill_id: int
    skill_name: Optional[str] = None
    level: str
    evaluation_date: date
    evaluated_by: Optional[int] = None
    comments: Optional[str] = None


# Training schemas
class TrainingCreate(BaseModel):
    """Schema for creating a training."""

    title: str = Field(..., max_length=255)
    training_date: date
    duration_hours: Optional[Decimal] = None
    trainer: Optional[str] = Field(None, max_length=200)
    comments: Optional[str] = None


class TrainingUpdate(BaseModel):
    """Schema for updating a training."""

    title: Optional[str] = Field(None, max_length=255)
    training_date: Optional[date] = None
    duration_hours: Optional[Decimal] = None
    trainer: Optional[str] = Field(None, max_length=200)
    comments: Optional[str] = None


class TrainingResponse(BaseModel):
    """Schema for training response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    beneficiary_id: int
    title: str
    training_date: date
    duration_hours: Optional[Decimal] = None
    trainer: Optional[str] = None
    comments: Optional[str] = None
    created_at: datetime
