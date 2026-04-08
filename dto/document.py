from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models.enums import DocumentStatus, RevisionStatus


class RevisionShortDTO(BaseModel):
    id: int
    revision_index: str = Field(..., max_length=10)
    revision_letter: str = Field(..., max_length=1)
    revision_number: int = Field(..., ge=0)
    status: RevisionStatus
    created_at: datetime
    file_path: Optional[str] = Field(None, max_length=1000)


class DocumentDetailDTO(BaseModel):
    id: int
    code: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=500)
    project_id: int
    status: DocumentStatus
    discipline: Optional[str] = Field(None, max_length=100)
    current_revision_id: Optional[int] = None
    revisions: List[RevisionShortDTO] = []


class DocumentListDTO(BaseModel):
    id: int
    code: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=500)
    project_id: int
    status: DocumentStatus
    discipline: Optional[str] = Field(None, max_length=100)
    current_revision_id: Optional[int] = None
