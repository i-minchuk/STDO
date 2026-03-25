from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .enums import DocumentStatus


@dataclass
class Document:
    id: int
    project_id: int
    code: str
    title: str
    discipline: Optional[str]
    status: DocumentStatus
    current_revision_id: Optional[int]
    created_by: int
    created_at: datetime