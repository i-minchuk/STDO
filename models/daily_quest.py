from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class DailyQuest:
    id: int
    user_id: int
    quest_type: str
    title: str
    description: str
    target_count: int
    current_count: int
    reward_points: int
    reward_xp: int
    date: date
    is_completed: bool
    completed_at: Optional[datetime] = None

    @staticmethod
    def from_row(row: dict) -> DailyQuest:
        return DailyQuest(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            quest_type=row["quest_type"],
            title=row["title"],
            description=row["description"],
            target_count=int(row["target_count"]),
            current_count=int(row["current_count"]),
            reward_points=int(row["reward_points"]),
            reward_xp=int(row["reward_xp"]),
            date=row["date"],
            is_completed=bool(row["is_completed"]),
            completed_at=row.get("completed_at"),
        )