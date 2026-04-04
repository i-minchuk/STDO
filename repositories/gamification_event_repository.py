from typing import Optional, Sequence, Dict, Any
from datetime import datetime

from db.database import Database
from models.gamification_event import GamificationEvent


class GamificationEventRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = """
        id, user_id, project_id, event_type, points_delta, xp_delta,
        metadata, created_at, action_key, ref_doc_id, ref_task_id, comment
    """

    def insert(
        self,
        user_id: int,
        event_type: str,
        points_delta: int,
        xp_delta: int = 0,
        project_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        action_key: Optional[str] = None,
        ref_doc_id: Optional[int] = None,
        ref_task_id: Optional[int] = None,
        comment: Optional[str] = None,
    ) -> GamificationEvent:
        row = self._db.fetch_one(
            f"""
            INSERT INTO gamification_events
            (user_id, project_id, event_type, points_delta, xp_delta,
             metadata, action_key, ref_doc_id, ref_task_id, comment)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING {self._COLUMNS}
            """,
            (
                user_id, project_id, event_type, points_delta, xp_delta,
                metadata or {}, action_key, ref_doc_id, ref_task_id, comment,
            ),
        )
        return self._row_to_model(row)

    def get_user_score(self, user_id: int) -> int:
        row = self._db.fetch_one(
            "SELECT COALESCE(SUM(points_delta), 0) AS score FROM gamification_events WHERE user_id = %s",
            (user_id,),
        )
        return int(row["score"]) if row else 0

    def get_user_events(self, user_id: int, limit: int = 50) -> Sequence[GamificationEvent]:
        rows = self._db.fetch_all(
            f"""
            SELECT {self._COLUMNS} FROM gamification_events
            WHERE user_id = %s ORDER BY created_at DESC LIMIT %s
            """,
            (user_id, limit),
        )
        return [self._row_to_model(r) for r in rows]

    def get_user_event_count(self, user_id: int, event_type: str) -> int:
        row = self._db.fetch_one(
            "SELECT COUNT(*) AS count FROM gamification_events WHERE user_id = %s AND event_type = %s",
            (user_id, event_type),
        )
        return int(row["count"]) if row else 0

    @staticmethod
    def _row_to_model(row: dict) -> GamificationEvent:
        return GamificationEvent(
            id=row["id"], user_id=row["user_id"], project_id=row.get("project_id"),
            event_type=row["event_type"], points_delta=row["points_delta"],
            xp_delta=row["xp_delta"], metadata=row.get("metadata", {}),
            created_at=row["created_at"], action_key=row.get("action_key"),
            ref_doc_id=row.get("ref_doc_id"), ref_task_id=row.get("ref_task_id"),
            comment=row.get("comment"),
        )