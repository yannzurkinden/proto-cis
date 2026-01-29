"""Skill reference management and beneficiary skill evaluation endpoints."""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_management, require_msp_or_above
from app.models.user import User
from app.repositories.beneficiary_repository import BeneficiaryRepository
from app.repositories.skill_repository import SkillRepository
from app.schemas.skill import (
    BeneficiarySkillEvaluate,
    BeneficiarySkillResponse,
    SkillCreate,
    SkillResponse,
    SkillUpdate,
    TrainingCreate,
    TrainingResponse,
    TrainingUpdate,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


# --- Skill Reference CRUD ---


@router.get("", response_model=list[SkillResponse])
async def list_skills(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    active_only: bool = True,
):
    """List all reference skills."""
    skill_repo = SkillRepository(db)
    skills = await skill_repo.get_all_active()
    return [SkillResponse.model_validate(s) for s in skills]


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
):
    """Create a new reference skill."""
    skill_repo = SkillRepository(db)
    skill = await skill_repo.create(skill_data.model_dump())
    return SkillResponse.model_validate(skill)


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
):
    """Update a reference skill."""
    skill_repo = SkillRepository(db)
    skill = await skill_repo.get_by_id(skill_id)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    update_data = skill_data.model_dump(exclude_unset=True)
    skill = await skill_repo.update(skill, update_data)
    return SkillResponse.model_validate(skill)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_management)],
):
    """Delete (deactivate) a reference skill."""
    skill_repo = SkillRepository(db)
    skill = await skill_repo.get_by_id(skill_id)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    # Soft delete by deactivating
    await skill_repo.update(skill, {"is_active": False})


# --- Beneficiary Skill Matrix ---


@router.get(
    "/beneficiaries/{beneficiary_id}/skills",
    response_model=list[BeneficiarySkillResponse],
)
async def get_beneficiary_skills(
    beneficiary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get the skill matrix for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    skill_repo = SkillRepository(db)
    evaluations = await skill_repo.get_beneficiary_skills(beneficiary_id)

    items = []
    for evaluation in evaluations:
        items.append(
            BeneficiarySkillResponse(
                id=evaluation.id,
                skill_id=evaluation.skill_id,
                skill_name=evaluation.skill.name if evaluation.skill else None,
                level=evaluation.level,
                evaluation_date=evaluation.evaluation_date,
                evaluated_by=evaluation.evaluated_by,
                comments=evaluation.comments,
            )
        )

    return items


@router.put(
    "/beneficiaries/{beneficiary_id}/skills/{skill_id}",
    response_model=BeneficiarySkillResponse,
)
async def evaluate_beneficiary_skill(
    beneficiary_id: int,
    skill_id: int,
    evaluation_data: BeneficiarySkillEvaluate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Evaluate a skill for a beneficiary (create or update evaluation)."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    skill_repo = SkillRepository(db)
    skill = await skill_repo.get_by_id(skill_id)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    evaluation = await skill_repo.evaluate_skill(
        beneficiary_id=beneficiary_id,
        skill_id=skill_id,
        level=evaluation_data.level,
        evaluated_by=current_user.id,
        comments=evaluation_data.comments,
    )

    return BeneficiarySkillResponse(
        id=evaluation.id,
        skill_id=evaluation.skill_id,
        skill_name=evaluation.skill.name if evaluation.skill else None,
        level=evaluation.level,
        evaluation_date=evaluation.evaluation_date,
        evaluated_by=evaluation.evaluated_by,
        comments=evaluation.comments,
    )


# --- Trainings ---


@router.get(
    "/beneficiaries/{beneficiary_id}/trainings",
    response_model=list[TrainingResponse],
)
async def list_trainings(
    beneficiary_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """List all trainings for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    skill_repo = SkillRepository(db)
    trainings = await skill_repo.get_trainings(beneficiary_id)
    return [TrainingResponse.model_validate(t) for t in trainings]


@router.post(
    "/beneficiaries/{beneficiary_id}/trainings",
    response_model=TrainingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_training(
    beneficiary_id: int,
    training_data: TrainingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Create a training record for a beneficiary."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    skill_repo = SkillRepository(db)
    training = await skill_repo.create_training(
        beneficiary_id=beneficiary_id,
        data=training_data.model_dump(),
    )
    return TrainingResponse.model_validate(training)


@router.put(
    "/beneficiaries/{beneficiary_id}/trainings/{training_id}",
    response_model=TrainingResponse,
)
async def update_training(
    beneficiary_id: int,
    training_id: int,
    training_data: TrainingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update a training record."""
    skill_repo = SkillRepository(db)
    training = await skill_repo.get_training_by_id(training_id)

    if not training or training.beneficiary_id != beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found",
        )

    update_data = training_data.model_dump(exclude_unset=True)
    training = await skill_repo.update_training(training, update_data)
    return TrainingResponse.model_validate(training)


@router.delete(
    "/beneficiaries/{beneficiary_id}/trainings/{training_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_training(
    beneficiary_id: int,
    training_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Delete a training record."""
    skill_repo = SkillRepository(db)
    training = await skill_repo.get_training_by_id(training_id)

    if not training or training.beneficiary_id != beneficiary_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found",
        )

    await skill_repo.delete_training(training)
