from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Any

# Импорт UTC-aware datetime factory
from core.datetime_utils import utc_now


def _utc_now() -> datetime:
    """UTC-aware datetime для использования в default_factory."""
    return datetime.now(timezone.utc)


# lazy import для избежания циклической зависимости
from datetime import timezone


@dataclass
class Tender:
    id: int
    name: str
    customer: str
    deadline_date: date
    status: str  # draft, assessed, approved, rejected
    vdr_required: bool = False
    otk_required: bool = False
    logistics_complexity: str = "normal"
    notes: Optional[str] = None
    required_disciplines: list[str] = field(default_factory=list)
    team_size: Optional[int] = None
    expected_review_rounds: int = 1
    expected_remark_count: int = 0
    created_by: Optional[int] = None
    created_at: datetime = field(default_factory=utc_now)
    assessed_at: Optional[datetime] = None
    assessment_result: Optional[dict[str, Any]] = None

    @staticmethod
    def from_row(row: dict) -> Tender:
        return Tender(
            id=row["id"],
            name=row["name"],
            customer=row["customer"],
            deadline_date=row["deadline_date"],
            status=row["status"],
            vdr_required=row.get("vdr_required", False),
            otk_required=row.get("otk_required", False),
            logistics_complexity=row.get("logistics_complexity", "normal"),
            notes=row.get("notes"),
            required_disciplines=row.get("required_disciplines", []),
            team_size=row.get("team_size"),
            expected_review_rounds=row.get("expected_review_rounds", 1),
            expected_remark_count=row.get("expected_remark_count", 0),
            created_by=row.get("created_by"),
            created_at=row.get("created_at", utc_now()),
            assessed_at=row.get("assessed_at"),
            assessment_result=row.get("assessment_result"),
        )


@dataclass
class TenderDocument:
    id: int
    tender_id: int
    doc_type: str
    count: int
    hours_per_doc: float
    discipline: Optional[str] = None

    @staticmethod
    def from_row(row: dict) -> TenderDocument:
        return TenderDocument(
            id=row["id"],
            tender_id=row["tender_id"],
            doc_type=row["doc_type"],
            count=row["count"],
            hours_per_doc=float(row["hours_per_doc"]),
            discipline=row.get("discipline"),
        )
