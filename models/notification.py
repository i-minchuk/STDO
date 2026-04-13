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
    def from_row(row: dict) -> Notification:
        return Notification(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            type=row["type"],
            title=row["title"],
            message=row["message"],
            is_read=bool(row["is_read"]),
            created_at=row["created_at"],
            metadata=row.get("metadata"),
        )