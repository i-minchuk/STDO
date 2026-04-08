from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class DepartmentRanking:
    """Department-based ranking for gamification."""
    id: int
    department: str
    user_id: int
    username: str
    full_name: str
    score: int
    level: int
    level_title: str
    badges_count: int
    rank_in_department: int
    total_in_department: int
    period_start: date
    period_end: date
    is_current_period: bool

    @property
    def rank_percentage(self) -> float:
        """Percentage rank in department (1.0 = top, 0.0 = bottom)."""
        if self.total_in_department <= 1:
            return 1.0
        return 1.0 - ((self.rank_in_department - 1) / (self.total_in_department - 1))

    @staticmethod
    def from_row(row: dict) -> DepartmentRanking:
        return DepartmentRanking(
            id=row["id"], department=row["department"], user_id=row["user_id"],
            username=row["username"], full_name=row["full_name"], score=row["score"],
            level=row["level"], level_title=row["level_title"], badges_count=row["badges_count"],
            rank_in_department=row["rank_in_department"], total_in_department=row["total_in_department"],
            period_start=row["period_start"], period_end=row["period_end"],
            is_current_period=row["is_current_period"],
        )


@dataclass
class DepartmentStats:
    """Statistics for a department."""
    department: str
    total_users: int
    active_users: int
    average_score: float
    average_level: float
    total_badges: int
    top_performer: Optional[str] = None
    top_score: Optional[int] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None

    @staticmethod
    def from_row(row: dict) -> DepartmentStats:
        return DepartmentStats(
            department=row["department"], total_users=row["total_users"],
            active_users=row["active_users"], average_score=float(row["average_score"]),
            average_level=float(row["average_level"]), total_badges=row["total_badges"],
            top_performer=row.get("top_performer"), top_score=row.get("top_score"),
            period_start=row.get("period_start"), period_end=row.get("period_end"),
        )