from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class VDREntry:
    id: int
    project_id: int
    doc_number: str
    title: str
    discipline: Optional[str]
    responsible_contractor: Optional[str]
    latest_revision: Optional[str]
    latest_upload_date: Optional[datetime]
    status: Optional[str]
    is_auto_filled: bool
    updated_at: datetime

    @staticmethod
    def from_row(row: dict) -> VDREntry:
        return VDREntry(
            id=int(row["id"]),
            project_id=int(row["project_id"]),
            doc_number=row["doc_number"],
            title=row["title"],
            discipline=row.get("discipline"),
            responsible_contractor=row.get("responsible_contractor"),
            latest_revision=row.get("latest_revision"),
            latest_upload_date=row.get("latest_upload_date"),
            status=row.get("status"),
            is_auto_filled=bool(row.get("is_auto_filled", False)),
            updated_at=row["updated_at"],
        )


@dataclass
class MDREntry:
    id: int
    project_id: int
    doc_number: str
    title: str
    discipline: Optional[str]
    revision_current: Optional[str]
    planned_issue_date: Optional[date]
    actual_issue_date: Optional[date]
    status: Optional[str]
    is_auto_filled: bool
    updated_at: datetime

    @staticmethod
    def from_row(row: dict) -> MDREntry:
        return MDREntry(
            id=int(row["id"]),
            project_id=int(row["project_id"]),
            doc_number=row["doc_number"],
            title=row["title"],
            discipline=row.get("discipline"),
            revision_current=row.get("revision_current"),
            planned_issue_date=row.get("planned_issue_date"),
            actual_issue_date=row.get("actual_issue_date"),
            status=row.get("status"),
            is_auto_filled=bool(row.get("is_auto_filled", False)),
            updated_at=row["updated_at"],
        )