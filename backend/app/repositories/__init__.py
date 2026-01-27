"""Repository modules for database access."""

from app.repositories.user_repository import UserRepository
from app.repositories.unit_repository import UnitRepository
from app.repositories.beneficiary_repository import BeneficiaryRepository
from app.repositories.pai_repository import PAIRepository
from app.repositories.objective_repository import ObjectiveRepository
from app.repositories.journal_repository import JournalRepository
from app.repositories.document_repository import DocumentRepository

__all__ = [
    "UserRepository",
    "UnitRepository",
    "BeneficiaryRepository",
    "PAIRepository",
    "ObjectiveRepository",
    "JournalRepository",
    "DocumentRepository",
]
