"""Document repository for database operations."""

from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document model."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Document)

    async def get_all_filtered(
        self,
        skip: int = 0,
        limit: int = 20,
        beneficiary_id: Optional[int] = None,
        document_type: Optional[str] = None,
        confidentiality: Optional[str] = None,
    ) -> tuple[List[Document], int]:
        """Get all documents with filtering and pagination."""
        query = select(Document).where(Document.is_current == True)

        if beneficiary_id:
            query = query.where(Document.beneficiary_id == beneficiary_id)
        if document_type:
            query = query.where(Document.document_type == document_type)
        if confidentiality:
            query = query.where(Document.confidentiality == confidentiality)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Paginated query
        query = query.offset(skip).limit(limit).order_by(Document.uploaded_at.desc())
        result = await self.db.execute(query)
        documents = list(result.scalars().all())

        return documents, total

    async def get_by_beneficiary(self, beneficiary_id: int) -> List[Document]:
        """Get all documents for a beneficiary."""
        result = await self.db.execute(
            select(Document)
            .where(Document.beneficiary_id == beneficiary_id)
            .where(Document.is_current == True)
            .order_by(Document.uploaded_at.desc())
        )
        return list(result.scalars().all())

    async def create_document(
        self,
        data: dict,
        uploaded_by: int,
    ) -> Document:
        """Create a new document."""
        document = Document(uploaded_by=uploaded_by, **data)
        self.db.add(document)
        await self.db.flush()
        await self.db.refresh(document)
        return document

    async def create_new_version(
        self,
        original_document: Document,
        new_data: dict,
        uploaded_by: int,
    ) -> Document:
        """Create a new version of a document."""
        # Mark original as not current
        original_document.is_current = False

        # Create new version
        new_document = Document(
            beneficiary_id=original_document.beneficiary_id,
            document_type=original_document.document_type,
            document_date=original_document.document_date,
            confidentiality=original_document.confidentiality,
            description=original_document.description,
            version=original_document.version + 1,
            previous_version_id=original_document.id,
            uploaded_by=uploaded_by,
            **new_data,
        )
        self.db.add(new_document)
        await self.db.flush()
        await self.db.refresh(new_document)
        return new_document
