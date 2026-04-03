from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class RemarkResponse:
    id: int
    remark_id: int
    author_id: int
    author_name: str
    text: str
    created_at: datetime

    @staticmethod
    def from_row(row: tuple) -> RemarkResponse:
        return RemarkResponse(
            id=row[0], remark_id=row[1], author_id=row[2],
            author_name=row[3], text=row[4], created_at=row[5],
        )


@dataclass
class Remark:
    id: int
    project_id: int
    document_id: Optional[int]
    revision_id: Optional[int]
    author_id: Optional[int]
    author_name: Optional[str]
    assignee_id: Optional[int]
    assignee_name: Optional[str]
    source: str
    text: str
    status: str
    resolution_comment: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    responses: list[RemarkResponse] = field(default_factory=list)

    @staticmethod
    def from_row(row: tuple) -> Remark:
        return Remark(
            id=row[0], project_id=row[1], document_id=row[2],
            revision_id=row[3], author_id=row[4], author_name=row[5],
            assignee_id=row[6], assignee_name=row[7], source=row[8],
            text=row[9], status=row[10], resolution_comment=row[11],
            created_at=row[12], resolved_at=row[13],
        )