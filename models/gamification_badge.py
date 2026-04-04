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
    def from_row(row: tuple) -> GamificationBadge:
        return GamificationBadge(
            id=row[0], user_id=row[1], badge_id=row[2], name=row[3],
            description=row[4], awarded_at=row[5], metadata=row[6],
        )