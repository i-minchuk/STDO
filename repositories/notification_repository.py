from typing import Sequence, Dict, Any, Optional
from datetime import datetime

from db.database import Database
from models.notification import Notification
from repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for notifications with BaseRepository for CRUD operations.
    
    Migrated to BaseRepository to reduce boilerplate.
    Custom methods: insert, get_user_notifications, mark_as_read, get_unread_count
    """
    
    def __init__(self, db: Database) -> None:
        super().__init__(
            db=db,
            model_class=Notification,
            table_name="notifications",
            columns="id, user_id, type, title, message, is_read, created_at, metadata"
        )

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
            INSERT INTO {self._table_name}
            (user_id, type, title, message, metadata)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING {self._columns}
            """,
            (user_id, type, title, message, metadata or {}),
        )
        return self._row_to_model(row)

    def get_user_notifications(self, user_id: int, limit: int = 20) -> Sequence[Notification]:
        rows = self._db.fetch_all(
            f"SELECT {self._columns} FROM {self._table_name} WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit),
        )
        return [self._row_to_model(r) for r in rows]

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        result = self._db.execute(
            f"UPDATE {self._table_name} SET is_read = true WHERE id = %s AND user_id = %s",
            (notification_id, user_id),
        )
        return result > 0

    def get_unread_count(self, user_id: int) -> int:
        row = self._db.fetch_one(
            f"SELECT COUNT(*) AS count FROM {self._table_name} WHERE user_id = %s AND is_read = false",
            (user_id,),
        )
        return int(row["count"]) if row else 0

    # _row_to_model is inherited from BaseRepository