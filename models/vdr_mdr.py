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
    def from_row(row: tuple) -> VDREntry:
        return VDREntry(
            id=row[0], project_id=row[1], doc_number=row[2], title=row[3],
            discipline=row[4], responsible_contractor=row[5],
            latest_revision=row[6], latest_upload_date=row[7],
            status=row[8], is_auto_filled=row[9], updated_at=row[10],
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
    def from_row(row: tuple) -> MDREntry:
        return MDREntry(
            id=row[0], project_id=row[1], doc_number=row[2], title=row[3],
            discipline=row[4], revision_current=row[5],
            planned_issue_date=row[6], actual_issue_date=row[7],
            status=row[8], is_auto_filled=row[9], updated_at=row[10],
        )