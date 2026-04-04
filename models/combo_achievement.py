from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class ComboAchievement:
    id: int
    user_id: int
    combo_type: str  # 'tasks', 'documents', 'time_logged', etc.
    current_count: int
    max_count: int
    multiplier: float  # Bonus multiplier (1.5x, 2x, etc.)
    expires_at: date
    is_active: bool

    @staticmethod
    def from_row(row: dict) -> ComboAchievement:
        return ComboAchievement(
            id=row["id"], user_id=row["user_id"], combo_type=row["combo_type"],
            current_count=row["current_count"], max_count=row["max_count"],
            multiplier=row["multiplier"], expires_at=row["expires_at"],
            is_active=row["is_active"],
        )