"""Beneficiary management endpoints."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_msp_or_above
from app.models.journal import JournalEntry
from app.models.objective import Objective
from app.models.user import User
from app.repositories.beneficiary_repository import BeneficiaryRepository
from app.repositories.pai_repository import PAIRepository
from app.schemas.beneficiary import (
    BeneficiaryCreate,
    BeneficiaryListResponse,
    BeneficiaryResponse,
    BeneficiaryStats,
    BeneficiaryUpdate,
    ContactCreate,
    ContactResponse,
    ContactUpdate,
    CurrentPAI,
    MedicalDataResponse,
    MedicalDataUpdate,
    RiskBehaviorCreate,
    RiskBehaviorResponse,
    RiskBehaviorUpdate,
)
from app.schemas.common import PaginatedResponse
from app.utils.encryption import decrypt_data, encrypt_data

router = APIRouter()


@router.get("", response_model=PaginatedResponse[BeneficiaryListResponse])
async def list_beneficiaries(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    unit_id: int | None = None,
    referent_id: int | None = None,
    search: str | None = None,
    sort: str | None = None,
):
    """List all beneficiaries with filtering and pagination."""
    beneficiary_repo = BeneficiaryRepository(db)
    skip = (page - 1) * size

    # Apply unit filter based on user role
    if current_user.role == "MSP":
        referent_id = current_user.id
    elif current_user.role in ["RES"] and current_user.unit_id:
        unit_id = current_user.unit_id

    beneficiaries, total = await beneficiary_repo.get_all_filtered(
        skip=skip,
        limit=size,
        status=status,
        unit_id=unit_id,
        referent_id=referent_id,
        search=search,
        sort=sort,
    )

    # Build response -- batch query objective counts to avoid N+1
    beneficiary_ids = [b.id for b in beneficiaries]
    in_progress_map: dict[int, int] = {}
    overdue_map: dict[int, int] = {}

    if beneficiary_ids:
        in_progress_query = (
            select(Objective.beneficiary_id, func.count().label("cnt"))
            .where(
                Objective.beneficiary_id.in_(beneficiary_ids),
                Objective.status == "in_progress",
            )
            .group_by(Objective.beneficiary_id)
        )
        in_progress_result = await db.execute(in_progress_query)
        in_progress_map = {row.beneficiary_id: row.cnt for row in in_progress_result}

        overdue_query = (
            select(Objective.beneficiary_id, func.count().label("cnt"))
            .where(
                Objective.beneficiary_id.in_(beneficiary_ids),
                Objective.due_date < date.today(),
                Objective.status.in_(["pending", "in_progress"]),
            )
            .group_by(Objective.beneficiary_id)
        )
        overdue_result = await db.execute(overdue_query)
        overdue_map = {row.beneficiary_id: row.cnt for row in overdue_result}

    items = []
    for b in beneficiaries:
        items.append(
            BeneficiaryListResponse(
                id=b.id,
                first_name=b.first_name,
                last_name=b.last_name,
                date_of_birth=b.date_of_birth,
                photo_url=b.photo_url,
                status=b.status,
                unit_id=b.unit_id,
                unit_name=b.unit.name if b.unit else None,
                referent_id=b.referent_id,
                referent_name=b.referent.full_name if b.referent else None,
                entry_date=b.entry_date,
                occupation_rate=b.occupation_rate,
                objectives_in_progress=in_progress_map.get(b.id, 0),
                objectives_overdue=overdue_map.get(b.id, 0),
            )
        )

    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{beneficiary_id}", response_model=BeneficiaryResponse)
async def get_beneficiary(
    beneficiary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a specific beneficiary by ID."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id_with_relations(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    # Get active PAI
    pai_repo = PAIRepository(db)
    active_pai = await pai_repo.get_active_pai(beneficiary_id)

    current_pai = None
    if active_pai:
        current_pai = CurrentPAI(
            id=active_pai.id,
            status=active_pai.status,
            valid_from=active_pai.valid_from,
            valid_to=active_pai.valid_to,
        )

    # Get contacts
    contacts = [
        ContactResponse.model_validate(c) for c in beneficiary.contacts
    ]

    # Calculate beneficiary stats
    obj_stats_query = select(
        func.count().label("total"),
        func.count().filter(Objective.status == "achieved").label("achieved"),
        func.count().filter(Objective.status == "in_progress").label("in_progress"),
        func.count().filter(
            and_(
                Objective.due_date < date.today(),
                Objective.status.in_(["pending", "in_progress"]),
            )
        ).label("overdue"),
    ).where(Objective.beneficiary_id == beneficiary_id)
    obj_result = await db.execute(obj_stats_query)
    obj_row = obj_result.one()

    # Get last journal entry date
    last_journal_query = (
        select(JournalEntry.entry_date)
        .where(JournalEntry.beneficiary_id == beneficiary_id)
        .order_by(JournalEntry.entry_date.desc())
        .limit(1)
    )
    last_journal_scalar = (await db.execute(last_journal_query)).scalar_one_or_none()
    last_journal_date = last_journal_scalar.date() if last_journal_scalar else None

    beneficiary_stats = BeneficiaryStats(
        objectives_total=obj_row.total,
        objectives_achieved=obj_row.achieved,
        objectives_in_progress=obj_row.in_progress,
        objectives_overdue=obj_row.overdue,
        last_journal_entry=last_journal_date,
    )

    return BeneficiaryResponse(
        id=beneficiary.id,
        first_name=beneficiary.first_name,
        last_name=beneficiary.last_name,
        date_of_birth=beneficiary.date_of_birth,
        photo_url=beneficiary.photo_url,
        address=beneficiary.address,
        postal_code=beneficiary.postal_code,
        city=beneficiary.city,
        phone=beneficiary.phone,
        email=beneficiary.email,
        language=beneficiary.language,
        ai_number=beneficiary.ai_number,
        pension_type=beneficiary.pension_type,
        guardianship_status=beneficiary.guardianship_status,
        entry_date=beneficiary.entry_date,
        exit_date=beneficiary.exit_date,
        status=beneficiary.status,
        contract_type=beneficiary.contract_type,
        occupation_rate=beneficiary.occupation_rate,
        salary=beneficiary.salary,
        unit_id=beneficiary.unit_id,
        unit_name=beneficiary.unit.name if beneficiary.unit else None,
        referent_id=beneficiary.referent_id,
        referent_name=beneficiary.referent.full_name if beneficiary.referent else None,
        current_pai=current_pai,
        contacts=contacts,
        stats=beneficiary_stats,
        created_at=beneficiary.created_at,
        updated_at=beneficiary.updated_at,
    )


@router.post("", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
async def create_beneficiary(
    beneficiary_data: BeneficiaryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Create a new beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)

    data = beneficiary_data.model_dump()
    data["created_by"] = current_user.id

    beneficiary = await beneficiary_repo.create(data)

    return BeneficiaryResponse(
        id=beneficiary.id,
        first_name=beneficiary.first_name,
        last_name=beneficiary.last_name,
        date_of_birth=beneficiary.date_of_birth,
        photo_url=beneficiary.photo_url,
        address=beneficiary.address,
        postal_code=beneficiary.postal_code,
        city=beneficiary.city,
        phone=beneficiary.phone,
        email=beneficiary.email,
        language=beneficiary.language,
        ai_number=beneficiary.ai_number,
        pension_type=beneficiary.pension_type,
        guardianship_status=beneficiary.guardianship_status,
        entry_date=beneficiary.entry_date,
        exit_date=beneficiary.exit_date,
        status=beneficiary.status,
        contract_type=beneficiary.contract_type,
        occupation_rate=beneficiary.occupation_rate,
        salary=beneficiary.salary,
        unit_id=beneficiary.unit_id,
        referent_id=beneficiary.referent_id,
        created_at=beneficiary.created_at,
        updated_at=beneficiary.updated_at,
    )


@router.put("/{beneficiary_id}", response_model=BeneficiaryResponse)
async def update_beneficiary(
    beneficiary_id: int,
    beneficiary_data: BeneficiaryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    update_data = beneficiary_data.model_dump(exclude_unset=True)
    beneficiary = await beneficiary_repo.update(beneficiary, update_data)
    beneficiary = await beneficiary_repo.get_by_id_with_relations(beneficiary.id)

    return BeneficiaryResponse(
        id=beneficiary.id,
        first_name=beneficiary.first_name,
        last_name=beneficiary.last_name,
        date_of_birth=beneficiary.date_of_birth,
        photo_url=beneficiary.photo_url,
        address=beneficiary.address,
        postal_code=beneficiary.postal_code,
        city=beneficiary.city,
        phone=beneficiary.phone,
        email=beneficiary.email,
        language=beneficiary.language,
        ai_number=beneficiary.ai_number,
        pension_type=beneficiary.pension_type,
        guardianship_status=beneficiary.guardianship_status,
        entry_date=beneficiary.entry_date,
        exit_date=beneficiary.exit_date,
        status=beneficiary.status,
        contract_type=beneficiary.contract_type,
        occupation_rate=beneficiary.occupation_rate,
        salary=beneficiary.salary,
        unit_id=beneficiary.unit_id,
        unit_name=beneficiary.unit.name if beneficiary.unit else None,
        referent_id=beneficiary.referent_id,
        referent_name=beneficiary.referent.full_name if beneficiary.referent else None,
        created_at=beneficiary.created_at,
        updated_at=beneficiary.updated_at,
    )


# Medical data endpoints
@router.get("/{beneficiary_id}/medical", response_model=MedicalDataResponse)
async def get_medical_data(
    beneficiary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Get medical data for a beneficiary (restricted access)."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    # Check access: MSP can only access their own beneficiaries
    if current_user.role == "MSP" and beneficiary.referent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to medical data",
        )

    medical_data = await beneficiary_repo.get_medical_data(beneficiary_id)

    if not medical_data:
        return MedicalDataResponse(beneficiary_id=beneficiary_id)

    return MedicalDataResponse(
        beneficiary_id=beneficiary_id,
        medication=decrypt_data(medical_data.medication),
        restrictions=decrypt_data(medical_data.restrictions),
        allergies=decrypt_data(medical_data.allergies),
        medical_notes=decrypt_data(medical_data.medical_notes),
    )


@router.put("/{beneficiary_id}/medical", response_model=MedicalDataResponse)
async def update_medical_data(
    beneficiary_id: int,
    medical_data: MedicalDataUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update medical data for a beneficiary (restricted access)."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    # Check access: MSP can only access their own beneficiaries
    if current_user.role == "MSP" and beneficiary.referent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to medical data",
        )

    # Encrypt data before storing
    data = {}
    if medical_data.medication is not None:
        data["medication"] = encrypt_data(medical_data.medication)
    if medical_data.restrictions is not None:
        data["restrictions"] = encrypt_data(medical_data.restrictions)
    if medical_data.allergies is not None:
        data["allergies"] = encrypt_data(medical_data.allergies)
    if medical_data.medical_notes is not None:
        data["medical_notes"] = encrypt_data(medical_data.medical_notes)

    await beneficiary_repo.create_or_update_medical_data(
        beneficiary_id=beneficiary_id,
        data=data,
        updated_by=current_user.id,
    )

    return MedicalDataResponse(
        beneficiary_id=beneficiary_id,
        medication=medical_data.medication,
        restrictions=medical_data.restrictions,
        allergies=medical_data.allergies,
        medical_notes=medical_data.medical_notes,
    )


# Contact endpoints
@router.get("/{beneficiary_id}/contacts", response_model=list[ContactResponse])
async def list_contacts(
    beneficiary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """List all contacts for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    contacts = await beneficiary_repo.get_contacts(beneficiary_id)
    return [ContactResponse.model_validate(c) for c in contacts]


@router.post(
    "/{beneficiary_id}/contacts",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    beneficiary_id: int,
    contact_data: ContactCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Create a contact for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    contact = await beneficiary_repo.create_contact(
        beneficiary_id=beneficiary_id,
        data=contact_data.model_dump(),
    )
    return ContactResponse.model_validate(contact)


@router.put("/{beneficiary_id}/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    beneficiary_id: int,
    contact_id: int,
    contact_data: ContactUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update a contact."""
    beneficiary_repo = BeneficiaryRepository(db)
    contact = await beneficiary_repo.get_contact_by_id(contact_id)

    if not contact or contact.beneficiary_id != beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    contact = await beneficiary_repo.update_contact(
        contact=contact,
        data=contact_data.model_dump(exclude_unset=True),
    )
    return ContactResponse.model_validate(contact)


@router.delete("/{beneficiary_id}/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    beneficiary_id: int,
    contact_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Delete a contact."""
    beneficiary_repo = BeneficiaryRepository(db)
    contact = await beneficiary_repo.get_contact_by_id(contact_id)

    if not contact or contact.beneficiary_id != beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    await beneficiary_repo.delete_contact(contact)


# Risk behavior endpoints
@router.get("/{beneficiary_id}/risk-behaviors", response_model=list[RiskBehaviorResponse])
async def list_risk_behaviors(
    beneficiary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    active_only: bool = True,
):
    """List risk behaviors for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    risk_behaviors = await beneficiary_repo.get_risk_behaviors(
        beneficiary_id=beneficiary_id,
        active_only=active_only,
    )
    return [RiskBehaviorResponse.model_validate(r) for r in risk_behaviors]


@router.post(
    "/{beneficiary_id}/risk-behaviors",
    response_model=RiskBehaviorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_risk_behavior(
    beneficiary_id: int,
    risk_data: RiskBehaviorCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Create a risk behavior for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    risk = await beneficiary_repo.create_risk_behavior(
        beneficiary_id=beneficiary_id,
        data=risk_data.model_dump(),
        reported_by=current_user.id,
    )
    return RiskBehaviorResponse.model_validate(risk)


@router.put(
    "/{beneficiary_id}/risk-behaviors/{risk_id}",
    response_model=RiskBehaviorResponse,
)
async def update_risk_behavior(
    beneficiary_id: int,
    risk_id: int,
    risk_data: RiskBehaviorUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update a risk behavior."""
    beneficiary_repo = BeneficiaryRepository(db)
    risk = await beneficiary_repo.get_risk_behavior_by_id(risk_id)

    if not risk or risk.beneficiary_id != beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk behavior not found",
        )

    risk = await beneficiary_repo.update_risk_behavior(
        risk=risk,
        data=risk_data.model_dump(exclude_unset=True),
    )
    return RiskBehaviorResponse.model_validate(risk)
