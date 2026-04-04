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
    def from_row(row: tuple) -> GamificationEvent:
        return GamificationEvent(
            id=row[0], user_id=row[1], project_id=row[2], event_type=row[3],
            points_delta=row[4], xp_delta=row[5], metadata=row[6], created_at=row[7],
            action_key=row[8], ref_doc_id=row[9], ref_task_id=row[10], comment=row[11],
        )