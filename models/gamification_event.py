from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class GamificationEvent:
    id: int
    user_id: int
    project_id: Optional[int]
    event_type: str
    points_delta: int
    xp_delta: int
    metadata: Dict[str, Any]
    created_at: datetime
    action_key: Optional[str]
    ref_doc_id: Optional[int]
    ref_task_id: Optional[int]
    comment: Optional[str]

    @staticmethod
    def from_row(row: dict) -> GamificationEvent:
        return GamificationEvent(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            project_id=int(row["project_id"]) if row.get("project_id") else None,
            event_type=row["event_type"],
            points_delta=int(row["points_delta"]),
            xp_delta=int(row["xp_delta"]),
            metadata=row.get("metadata", {}),
            created_at=row["created_at"],
            action_key=row.get("action_key"),
            ref_doc_id=int(row["ref_doc_id"]) if row.get("ref_doc_id") else None,
            ref_task_id=int(row["ref_task_id"]) if row.get("ref_task_id") else None,
            comment=row.get("comment"),
        )