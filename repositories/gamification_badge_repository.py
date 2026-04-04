from typing import Sequence, Dict, Any, Optional
from datetime import datetime

from db.database import Database
from models.gamification_badge import GamificationBadge


class GamificationBadgeRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = "id, user_id, badge_id, name, description, awarded_at, metadata"

    def insert(
        self,
        user_id: int,
        badge_id: str,
        name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GamificationBadge:
        row = self._db.fetch_one(
            f"""
            INSERT INTO gamification_badges
            (user_id, badge_id, name, description, metadata)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING {self._COLUMNS}
            """,
            (user_id, badge_id, name, description, metadata or {}),
        )
        return self._row_to_model(row)

    def get_user_badges(self, user_id: int) -> Sequence[GamificationBadge]:
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM gamification_badges WHERE user_id = %s ORDER BY awarded_at DESC",
            (user_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def has_badge(self, user_id: int, badge_id: str) -> bool:
        row = self._db.fetch_one(
            "SELECT 1 FROM gamification_badges WHERE user_id = %s AND badge_id = %s",
            (user_id, badge_id),
        )
        return row is not None

    def award_badge_if_not_exists(
        self,
        user_id: int,
        badge_id: str,
        name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[GamificationBadge]:
        if self.has_badge(user_id, badge_id):
            return None
        return self.insert(user_id, badge_id, name, description, metadata)

    @staticmethod
    def _row_to_model(row: dict) -> GamificationBadge:
        return GamificationBadge(
            id=row["id"], user_id=row["user_id"], badge_id=row["badge_id"],
            name=row["name"], description=row["description"],
            awarded_at=row["awarded_at"], metadata=row.get("metadata", {}),
        )