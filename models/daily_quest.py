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
    def from_row(row: tuple) -> DailyQuest:
        return DailyQuest(
            id=row[0], user_id=row[1], quest_type=row[2], title=row[3],
            description=row[4], target_count=row[5], current_count=row[6],
            reward_points=row[7], reward_xp=row[8], date=row[9],
            is_completed=row[10], completed_at=row[11],
        )