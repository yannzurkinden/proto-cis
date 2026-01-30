"""Beneficiary-related schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BeneficiaryBase(BaseModel):
    """Base beneficiary schema."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    address: str | None = None
    postal_code: str | None = Field(None, max_length=10)
    city: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    language: str = "fr"

    ai_number: str | None = Field(None, max_length=50)
    pension_type: Literal["quarter", "half", "three_quarter", "full"] | None = None
    guardianship_status: str | None = None
    entry_date: date
    contract_type: str | None = None
    occupation_rate: Decimal | None = Field(None, ge=0, le=100)
    unit_id: int | None = None
    referent_id: int | None = None


class BeneficiaryCreate(BeneficiaryBase):
    """Schema for creating a beneficiary."""

    pass


class BeneficiaryUpdate(BaseModel):
    """Schema for updating a beneficiary."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    photo_url: str | None = None
    address: str | None = None
    postal_code: str | None = Field(None, max_length=10)
    city: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    language: str | None = None

    ai_number: str | None = Field(None, max_length=50)
    pension_type: Literal["quarter", "half", "three_quarter", "full"] | None = None
    guardianship_status: str | None = None
    entry_date: date | None = None
    exit_date: date | None = None
    status: Literal["active", "paused", "exited"] | None = None
    contract_type: str | None = None
    occupation_rate: Decimal | None = Field(None, ge=0, le=100)
    salary: Decimal | None = None
    unit_id: int | None = None
    referent_id: int | None = None


class BeneficiaryStats(BaseModel):
    """Statistics for a beneficiary."""

    objectives_total: int = 0
    objectives_achieved: int = 0
    objectives_in_progress: int = 0
    objectives_overdue: int = 0
    absence_rate_30d: float = 0.0
    last_journal_entry: date | None = None


class CurrentPAI(BaseModel):
    """Current PAI summary."""

    id: int
    status: str
    valid_from: date
    valid_to: date | None = None


class BeneficiaryResponse(BeneficiaryBase):
    """Schema for beneficiary response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_url: str | None = None
    exit_date: date | None = None
    status: str
    salary: Decimal | None = None
    unit_name: str | None = None
    referent_name: str | None = None
    current_pai: CurrentPAI | None = None
    stats: BeneficiaryStats | None = None
    contacts: list["ContactResponse"] | None = None
    created_at: datetime
    updated_at: datetime


class BeneficiaryListResponse(BaseModel):
    """Schema for beneficiary list item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    photo_url: str | None = None
    status: str
    unit_id: int | None = None
    unit_name: str | None = None
    referent_id: int | None = None
    referent_name: str | None = None
    entry_date: date
    occupation_rate: Decimal | None = None
    objectives_in_progress: int = 0
    objectives_overdue: int = 0


# Medical Data
class MedicalDataUpdate(BaseModel):
    """Schema for updating medical data."""

    medication: str | None = None
    restrictions: str | None = None
    allergies: str | None = None
    medical_notes: str | None = None


class MedicalDataResponse(BaseModel):
    """Schema for medical data response."""

    model_config = ConfigDict(from_attributes=True)

    beneficiary_id: int
    medication: str | None = None
    restrictions: str | None = None
    allergies: str | None = None
    medical_notes: str | None = None


# Contacts
class ContactBase(BaseModel):
    """Base contact schema."""

    contact_type: Literal["emergency", "doctor", "psychologist", "ai_referent", "other"]
    name: str = Field(..., min_length=1, max_length=200)
    organization: str | None = Field(None, max_length=200)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    notes: str | None = None
    is_emergency_contact: bool = False


class ContactCreate(ContactBase):
    """Schema for creating a contact."""

    pass


class ContactUpdate(BaseModel):
    """Schema for updating a contact."""

    contact_type: Literal["emergency", "doctor", "psychologist", "ai_referent", "other"] | None = None
    name: str | None = Field(None, min_length=1, max_length=200)
    organization: str | None = Field(None, max_length=200)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    address: str | None = None
    notes: str | None = None
    is_emergency_contact: bool | None = None


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
    preventive_measures: str | None = None
    reported_date: date


class RiskBehaviorCreate(RiskBehaviorBase):
    """Schema for creating a risk behavior."""

    pass


class RiskBehaviorUpdate(BaseModel):
    """Schema for updating a risk behavior."""

    risk_type: str | None = Field(None, max_length=50)
    description: str | None = None
    severity: Literal["low", "medium", "high", "critical"] | None = None
    preventive_measures: str | None = None
    is_active: bool | None = None


class RiskBehaviorResponse(RiskBehaviorBase):
    """Schema for risk behavior response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
