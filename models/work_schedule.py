from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class WorkSchedule:
    """System-wide work schedule configuration."""
    id: int
    name: str
    work_days: List[int]  # 0=Monday, 6=Sunday (e.g., [0,1,2,3,4] for Mon-Fri)
    start_time_hours: float  # e.g., 8.5 for 8:30
    end_time_hours: float    # e.g., 17.5 for 17:30
    lunch_duration_hours: float  # e.g., 1.0 for 1 hour
    is_default: bool = False

    @property
    def work_hours_per_day(self) -> float:
        """Calculate actual work hours per day."""
        total_hours = self.end_time_hours - self.start_time_hours
        return total_hours - self.lunch_duration_hours

    @property
    def work_hours_per_week(self) -> float:
        """Calculate work hours per week."""
        return self.work_hours_per_day * len(self.work_days)

    def is_work_day(self, weekday: int) -> bool:
        """Check if given weekday (0=Monday) is a work day."""
        return weekday in self.work_days

    @staticmethod
    def from_row(row: dict) -> WorkSchedule:
        return WorkSchedule(
            id=row["id"],
            name=row["name"],
            work_days=row["work_days"],  # Should be stored as JSON
            start_time_hours=float(row["start_time_hours"]),
            end_time_hours=float(row["end_time_hours"]),
            lunch_duration_hours=float(row["lunch_duration_hours"]),
            is_default=row.get("is_default", False),
        )
