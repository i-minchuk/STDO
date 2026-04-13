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
    def from_row(row: dict) -> RemarkResponse:
        return RemarkResponse(
            id=int(row["id"]),
            remark_id=int(row["remark_id"]),
            author_id=int(row["author_id"]),
            author_name=row["author_name"],
            text=row["text"],
            created_at=row["created_at"],
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
    def from_row(row: dict) -> Remark:
        return Remark(
            id=int(row["id"]),
            project_id=int(row["project_id"]),
            document_id=int(row["document_id"]) if row.get("document_id") else None,
            revision_id=int(row["revision_id"]) if row.get("revision_id") else None,
            author_id=int(row["author_id"]) if row.get("author_id") else None,
            author_name=row.get("author_name"),
            assignee_id=int(row["assignee_id"]) if row.get("assignee_id") else None,
            assignee_name=row.get("assignee_name"),
            source=row["source"],
            text=row["text"],
            status=row["status"],
            resolution_comment=row.get("resolution_comment"),
            created_at=row["created_at"],
            resolved_at=row.get("resolved_at"),
        )