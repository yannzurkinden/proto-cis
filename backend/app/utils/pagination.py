"""Pagination utilities."""

from math import ceil
from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int


def paginate(
    items: List[T],
    total: int,
    page: int,
    size: int,
) -> PaginatedResponse[T]:
    """Create a paginated response."""
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if size > 0 else 0,
    )


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = 1
    size: int = 20

    @property
    def skip(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Return size as limit."""
        return self.size
