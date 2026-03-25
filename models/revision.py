from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .enums import RevisionStatus


@dataclass
class DocumentRevision:
    id: int
    document_id: int
    revision_index: str
    revision_letter: str
    revision_number: int
    version_number: int
    status: RevisionStatus
    file_path: str
    change_log: Optional[str]
    created_by: int
    created_at: datetime
    approved_by: Optional[int]
    approved_at: Optional[datetime]