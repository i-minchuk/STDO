from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Notification:
    id: int
    user_id: int
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    metadata: Optional[dict] = None

    @staticmethod
    def from_row(row: tuple) -> Notification:
        return Notification(
            id=row[0], user_id=row[1], type=row[2], title=row[3],
            message=row[4], is_read=row[5], created_at=row[6],
            metadata=row[7],
        )