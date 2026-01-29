"""Journal entry management endpoints."""

from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_msp_or_above
from app.models.user import User
from app.repositories.journal_repository import JournalRepository
from app.repositories.beneficiary_repository import BeneficiaryRepository
from app.schemas.journal import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
    JournalCategoryResponse,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[JournalEntryResponse])
async def list_journal_entries(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    beneficiary_id: Optional[int] = None,
    author_id: Optional[int] = None,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,
):
    """List all journal entries with filtering and pagination."""
    journal_repo = JournalRepository(db)
    skip = (page - 1) * size

    # Parse category IDs if provided
    category_ids = None
    if category:
        category_ids = [int(c) for c in category.split(",")]

    # Parse tags if provided
    tag_list = None
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]

    # Apply unit filter based on user role
    unit_id = None
    if current_user.role == "MSP":
        author_id = current_user.id
    elif current_user.role in ["RES"] and current_user.unit_id:
        unit_id = current_user.unit_id

    entries, total = await journal_repo.get_all_filtered(
        skip=skip,
        limit=size,
        beneficiary_id=beneficiary_id,
        author_id=author_id,
        category_ids=category_ids,
        date_from=date_from,
        date_to=date_to,
        search=search,
        tags=tag_list,
        unit_id=unit_id,
    )

    # Batch load author names to avoid N+1 queries
    author_ids = list({entry.author_id for entry in entries})
    author_map: dict[int, str] = {}
    if author_ids:
        author_query = select(User.id, User.first_name, User.last_name).where(
            User.id.in_(author_ids)
        )
        author_result = await db.execute(author_query)
        author_map = {
            row.id: f"{row.first_name} {row.last_name}" for row in author_result
        }

    items = []
    for entry in entries:
        categories = [
            JournalCategoryResponse.model_validate(ec.category)
            for ec in entry.categories
        ]
        entry_tags = [t.tag for t in entry.tags]

        items.append(
            JournalEntryResponse(
                id=entry.id,
                beneficiary_id=entry.beneficiary_id,
                beneficiary_name=entry.beneficiary.full_name if entry.beneficiary else None,
                author_id=entry.author_id,
                author_name=author_map.get(entry.author_id),
                title=entry.title,
                content=entry.content,
                entry_date=entry.entry_date,
                visibility=entry.visibility,
                categories=categories,
                tags=entry_tags,
                attachments_count=0,  # Document attachment counting not yet integrated
                created_at=entry.created_at,
                updated_at=entry.updated_at,
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


@router.get("/categories", response_model=list[JournalCategoryResponse])
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """List all journal categories."""
    journal_repo = JournalRepository(db)
    categories = await journal_repo.get_all_categories()
    return [JournalCategoryResponse.model_validate(c) for c in categories]


@router.get("/tags", response_model=list[str])
async def list_tags(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    beneficiary_id: Optional[int] = None,
):
    """List all unique tags used in journal entries."""
    if beneficiary_id:
        journal_repo = JournalRepository(db)
        return await journal_repo.get_tags_for_beneficiary(beneficiary_id)
    return []


@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get a specific journal entry by ID."""
    journal_repo = JournalRepository(db)
    entry = await journal_repo.get_by_id_with_relations(entry_id)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )

    # Load author name
    author_result = await db.execute(
        select(User).where(User.id == entry.author_id)
    )
    author = author_result.scalar_one_or_none()
    author_name = author.full_name if author else None

    categories = [
        JournalCategoryResponse.model_validate(ec.category)
        for ec in entry.categories
    ]
    entry_tags = [t.tag for t in entry.tags]

    return JournalEntryResponse(
        id=entry.id,
        beneficiary_id=entry.beneficiary_id,
        beneficiary_name=entry.beneficiary.full_name if entry.beneficiary else None,
        author_id=entry.author_id,
        author_name=author_name,
        title=entry.title,
        content=entry.content,
        entry_date=entry.entry_date,
        visibility=entry.visibility,
        categories=categories,
        tags=entry_tags,
        attachments_count=0,  # Document attachment counting not yet integrated
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


@router.post("", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Create a new journal entry."""
    beneficiary_repo = BeneficiaryRepository(db)
    beneficiary = await beneficiary_repo.get_by_id(entry_data.beneficiary_id)

    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found",
        )

    journal_repo = JournalRepository(db)

    data = entry_data.model_dump(exclude={"category_ids", "tags"})
    entry = await journal_repo.create_entry(
        data=data,
        author_id=current_user.id,
        category_ids=entry_data.category_ids,
        tags=entry_data.tags,
    )

    entry = await journal_repo.get_by_id_with_relations(entry.id)

    categories = [
        JournalCategoryResponse.model_validate(ec.category)
        for ec in entry.categories
    ]
    entry_tags = [t.tag for t in entry.tags]

    return JournalEntryResponse(
        id=entry.id,
        beneficiary_id=entry.beneficiary_id,
        beneficiary_name=entry.beneficiary.full_name if entry.beneficiary else None,
        author_id=entry.author_id,
        author_name=current_user.full_name,
        title=entry.title,
        content=entry.content,
        entry_date=entry.entry_date,
        visibility=entry.visibility,
        categories=categories,
        tags=entry_tags,
        attachments_count=0,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


@router.put("/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: int,
    entry_data: JournalEntryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update a journal entry."""
    journal_repo = JournalRepository(db)
    entry = await journal_repo.get_by_id(entry_id)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )

    # Only author can edit their entries (or admin)
    if entry.author_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author can edit this entry",
        )

    data = entry_data.model_dump(exclude={"category_ids", "tags"}, exclude_unset=True)
    entry = await journal_repo.update_entry(
        entry=entry,
        data=data,
        category_ids=entry_data.category_ids,
        tags=entry_data.tags,
    )

    entry = await journal_repo.get_by_id_with_relations(entry.id)

    # Load author name
    update_author_result = await db.execute(
        select(User).where(User.id == entry.author_id)
    )
    update_author = update_author_result.scalar_one_or_none()
    update_author_name = update_author.full_name if update_author else None

    categories = [
        JournalCategoryResponse.model_validate(ec.category)
        for ec in entry.categories
    ]
    entry_tags = [t.tag for t in entry.tags]

    return JournalEntryResponse(
        id=entry.id,
        beneficiary_id=entry.beneficiary_id,
        beneficiary_name=entry.beneficiary.full_name if entry.beneficiary else None,
        author_id=entry.author_id,
        author_name=update_author_name,
        title=entry.title,
        content=entry.content,
        entry_date=entry.entry_date,
        visibility=entry.visibility,
        categories=categories,
        tags=entry_tags,
        attachments_count=0,  # Document attachment counting not yet integrated
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_entry(
    entry_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Delete a journal entry."""
    journal_repo = JournalRepository(db)
    entry = await journal_repo.get_by_id(entry_id)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )

    # Only author can delete their entries (or admin)
    if entry.author_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author can delete this entry",
        )

    await journal_repo.delete(entry)
