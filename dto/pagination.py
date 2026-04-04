"""Pagination DTOs for list endpoints."""
from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination query parameters."""

    limit: int = Field(default=20, gt=0, le=1000, description="Number of items per page")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    limit: int = Field(description="Number of items per page")
    offset: int = Field(description="Number of items skipped")

    @property
    def page(self) -> int:
        """Calculate page number (1-indexed)."""
        return (self.offset // self.limit) + 1

    @property
    def pages(self) -> int:
        """Calculate total number of pages."""
        import math
        return math.ceil(self.total / self.limit) if self.total > 0 else 0

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.offset + self.limit < self.total

    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.offset > 0
