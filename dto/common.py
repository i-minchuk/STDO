from pydantic import BaseModel
from typing import Optional


class ProjectShortDTO(BaseModel):
    id: int
    code: str
    name: str
    status: str


class DocumentShortDTO(BaseModel):
    id: int
    project_id: int
    project_code: Optional[str] = None
    code: str
    title: str
    status: str
    current_revision_id: Optional[int] = None