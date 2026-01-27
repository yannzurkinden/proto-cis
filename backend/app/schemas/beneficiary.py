"""Beneficiary-related schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BeneficiaryBase(BaseModel):
    """Base beneficiary schema."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    address: Optional[str] = None
    postal_code: Optional[str] = Field(None, max_length=10)
    city: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    language: str = "fr"

    ai_number: Optional[str] = Field(None, max_length=50)
    pension_type: Optional[Literal["quarter", "half", "three_quarter", "full"]] = None
    guardianship_status: Optional[str] = None
    entry_date: date
    contract_type: Optional[str] = None
    occupation_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    unit_id: Optional[int] = None
    referent_id: Optional[int] = None


class BeneficiaryCreate(BeneficiaryBase):
    """Schema for creating a beneficiary."""

    pass


class BeneficiaryUpdate(BaseModel):
    """Schema for updating a beneficiary."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    photo_url: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = Field(None, max_length=10)
    city: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    language: Optional[str] = None

    ai_number: Optional[str] = Field(None, max_length=50)
    pension_type: Optional[Literal["quarter", "half", "three_quarter", "full"]] = None
    guardianship_status: Optional[str] = None
    entry_date: Optional[date] = None
    exit_date: Optional[date] = None
    status: Optional[Literal["active", "paused", "exited"]] = None
    contract_type: Optional[str] = None
    occupation_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    salary: Optional[Decimal] = None
    unit_id: Optional[int] = None
    referent_id: Optional[int] = None


class BeneficiaryStats(BaseModel):
    """Statistics for a beneficiary."""

    objectives_total: int = 0
    objectives_achieved: int = 0
    objectives_in_progress: int = 0
    objectives_overdue: int = 0
    absence_rate_30d: float = 0.0
    last_journal_entry: Optional[date] = None


class CurrentPAI(BaseModel):
    """Current PAI summary."""

    id: int
    status: str
    valid_from: date
    valid_to: Optional[date] = None


class BeneficiaryResponse(BeneficiaryBase):
    """Schema for beneficiary response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_url: Optional[str] = None
    exit_date: Optional[date] = None
    status: str
    salary: Optional[Decimal] = None
    unit_name: Optional[str] = None
    referent_name: Optional[str] = None
    current_pai: Optional[CurrentPAI] = None
    stats: Optional[BeneficiaryStats] = None
    contacts: Optional[List["ContactResponse"]] = None
    created_at: datetime
    updated_at: datetime


class BeneficiaryListResponse(BaseModel):
    """Schema for beneficiary list item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    photo_url: Optional[str] = None
    status: str
    unit_id: Optional[int] = None
    unit_name: Optional[str] = None
    referent_id: Optional[int] = None
    referent_name: Optional[str] = None
    entry_date: date
    occupation_rate: Optional[Decimal] = None
    objectives_in_progress: int = 0
    objectives_overdue: int = 0


# Medical Data
class MedicalDataUpdate(BaseModel):
    """Schema for updating medical data."""

    medication: Optional[str] = None
    restrictions: Optional[str] = None
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None


class MedicalDataResponse(BaseModel):
    """Schema for medical data response."""

    model_config = ConfigDict(from_attributes=True)

    beneficiary_id: int
    medication: Optional[str] = None
    restrictions: Optional[str] = None
    allergies: Optional[str] = None
    medical_notes: Optional[str] = None


# Contacts
class ContactBase(BaseModel):
    """Base contact schema."""

    contact_type: Literal["emergency", "doctor", "psychologist", "ai_referent", "other"]
    name: str = Field(..., min_length=1, max_length=200)
    organization: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_emergency_contact: bool = False


class ContactCreate(ContactBase):
    """Schema for creating a contact."""

    pass


class ContactUpdate(BaseModel):
    """Schema for updating a contact."""

    contact_type: Optional[Literal["emergency", "doctor", "psychologist", "ai_referent", "other"]] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    organization: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_emergency_contact: Optional[bool] = None


class ContactResponse(ContactBase):
    """Schema for contact response."""

    model_config = ConfigDict(from_attributes=True)

    id: int


# Risk Behaviors
class RiskBehaviorBase(BaseModel):
    """Base risk behavior schema."""

    risk_type: str = Field(..., max_length=50)
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    preventive_measures: Optional[str] = None
    reported_date: date


class RiskBehaviorCreate(RiskBehaviorBase):
    """Schema for creating a risk behavior."""

    pass


class RiskBehaviorUpdate(BaseModel):
    """Schema for updating a risk behavior."""

    risk_type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None
    preventive_measures: Optional[str] = None
    is_active: Optional[bool] = None


class RiskBehaviorResponse(RiskBehaviorBase):
    """Schema for risk behavior response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
