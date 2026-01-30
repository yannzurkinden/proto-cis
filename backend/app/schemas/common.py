"""Common schemas used across the API."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""

    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class Message(BaseModel):
    """Simple message response."""

    message: str


class ErrorDetail(BaseModel):
    """Error detail for validation errors."""

    field: str
    message: str


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str
    code: str | None = None
    errors: list[ErrorDetail] | None = None
