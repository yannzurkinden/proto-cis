"""Document management endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_msp_or_above
from app.models.user import User
from app.repositories.beneficiary_repository import BeneficiaryRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.common import PaginatedResponse
from app.schemas.document import DocumentResponse, DocumentUpdate

router = APIRouter()


@router.get("", response_model=PaginatedResponse[DocumentResponse])
async def list_documents(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    beneficiary_id: int | None = None,
    document_type: str | None = None,
    confidentiality: str | None = None,
):
    """List all documents with filtering and pagination."""
    document_repo = DocumentRepository(db)
    skip = (page - 1) * size

    documents, total = await document_repo.get_all_filtered(
        skip=skip,
        limit=size,
        beneficiary_id=beneficiary_id,
        document_type=document_type,
        confidentiality=confidentiality,
    )

    pages = (total + size - 1) // size if size > 0 else 0

    return PaginatedResponse(
        items=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/types")
async def list_document_types(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """List available document types."""
    return [
        "pai", "medical", "administrative", "contract",
        "report", "certificate", "correspondence", "other",
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get document metadata by ID."""
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check access based on confidentiality
    if document.confidentiality == "highly_confidential" and current_user.role not in ["ADMIN", "RUA"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to highly confidential document",
        )

    return DocumentResponse.model_validate(document)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
    file: UploadFile = File(...),  # noqa: B008
    beneficiary_id: int | None = Form(None),
    document_type: str = Form(...),
    document_date: str | None = Form(None),
    confidentiality: str = Form("standard"),
    description: str | None = Form(None),
):
    """Upload a new document."""
    # Validate beneficiary exists if provided
    if beneficiary_id:
        beneficiary_repo = BeneficiaryRepository(db)
        beneficiary = await beneficiary_repo.get_by_id(beneficiary_id)
        if not beneficiary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beneficiary not found",
            )

    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    stored_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())

    # In a real implementation, this would upload to MinIO
    file_path = f"documents/{stored_filename}"

    # Read file content (in real implementation, stream to storage)
    content = await file.read()
    file_size = len(content)

    document_repo = DocumentRepository(db)
    document = await document_repo.create_document(
        data={
            "beneficiary_id": beneficiary_id,
            "original_filename": file.filename,
            "stored_filename": stored_filename,
            "file_path": file_path,
            "file_size": file_size,
            "mime_type": file.content_type,
            "document_type": document_type,
            "document_date": document_date,
            "confidentiality": confidentiality,
            "description": description,
        },
        uploaded_by=current_user.id,
    )

    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Download a document."""
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check access based on confidentiality
    if document.confidentiality == "highly_confidential" and current_user.role not in ["ADMIN", "RUA"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to highly confidential document",
        )

    # In a real implementation, this would stream from MinIO
    # For now, return a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="File storage not yet configured",
    )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Update document metadata."""
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    update_data = document_data.model_dump(exclude_unset=True)
    document = await document_repo.update(document, update_data)

    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_msp_or_above)],
):
    """Delete a document."""
    document_repo = DocumentRepository(db)
    document = await document_repo.get_by_id(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # In a real implementation, also delete from MinIO
    await document_repo.delete(document)
