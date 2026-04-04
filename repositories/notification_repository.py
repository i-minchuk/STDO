from typing import Sequence, Dict, Any, Optional
from datetime import datetime

from db.database import Database
from models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = "id, user_id, type, title, message, is_read, created_at, metadata"

    def insert(
        self,
        user_id: int,
        type: str,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        row = self._db.fetch_one(
            f"""
            INSERT INTO notifications
            (user_id, type, title, message, metadata)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING {self._COLUMNS}
            """,
            (user_id, type, title, message, metadata or {}),
        )
        return self._row_to_model(row)

    def get_user_notifications(self, user_id: int, limit: int = 20) -> Sequence[Notification]:
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit),
        )
        return [self._row_to_model(r) for r in rows]

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        result = self._db.execute(
            "UPDATE notifications SET is_read = true WHERE id = %s AND user_id = %s",
            (notification_id, user_id),
        )
        return result > 0

    def get_unread_count(self, user_id: int) -> int:
        row = self._db.fetch_one(
            "SELECT COUNT(*) AS count FROM notifications WHERE user_id = %s AND is_read = false",
            (user_id,),
        )
        return int(row["count"]) if row else 0

    @staticmethod
    def _row_to_model(row: dict) -> Notification:
        return Notification(
            id=row["id"], user_id=row["user_id"], type=row["type"],
            title=row["title"], message=row["message"],
            is_read=row["is_read"], created_at=row["created_at"],
            metadata=row.get("metadata", {}),
        )