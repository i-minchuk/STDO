from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ProjectShortDTO(BaseModel):
    id: int
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    status: str

    @field_validator('code')
    @classmethod
    def validate_code_alphanumeric(cls, v):
        """Code must contain only letters, numbers, underscore, hyphen."""
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError('Code must be alphanumeric with hyphens/underscores only')
        return v


class DocumentShortDTO(BaseModel):
    id: int
    project_id: int
    project_code: Optional[str] = Field(None, max_length=50)
    code: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=500)
    status: str
    current_revision_id: Optional[int] = None

    @field_validator('code')
    @classmethod
    def validate_code_alphanumeric(cls, v):
        """Code must contain only letters, numbers, underscore, hyphen."""
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError('Code must be alphanumeric with hyphens/underscores only')
        return v