from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class GamificationBadge:
    id: int
    user_id: int
    badge_id: str
    name: str
    description: str
    awarded_at: datetime
    metadata: Optional[dict] = None

    @staticmethod
    def from_row(row: dict) -> GamificationBadge:
        return GamificationBadge(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            badge_id=row["badge_id"],
            name=row["name"],
            description=row["description"],
            awarded_at=row["awarded_at"],
            metadata=row.get("metadata"),
        )