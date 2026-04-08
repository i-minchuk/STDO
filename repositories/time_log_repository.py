from typing import Optional, Sequence
from datetime import date

from db.database import Database
from models.time_log import TimeLog


class TimeLogRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = """
        id, user_id, project_id, document_id, task_id, day, hours, description
    """

    def get_by_id(self, log_id: int) -> Optional[TimeLog]:
        row = self._db.fetch_one(
            f"SELECT {self._COLUMNS} FROM time_logs WHERE id = %s",
            (log_id,)
        )
        return self._row_to_model(row) if row else None

    def get_by_user_id(self, user_id: int, date_from: date, date_to: date) -> Sequence[TimeLog]:
        rows = self._db.fetch_all(
            f"""
            SELECT {self._COLUMNS} FROM time_logs
            WHERE user_id = %s AND day >= %s AND day <= %s
            ORDER BY day DESC
            """,
            (user_id, date_from, date_to)
        )
        return [self._row_to_model(r) for r in rows]

    def get_by_project_id(self, project_id: int, date_from: date, date_to: date) -> Sequence[TimeLog]:
        rows = self._db.fetch_all(
            f"""
            SELECT {self._COLUMNS} FROM time_logs
            WHERE project_id = %s AND day >= %s AND day <= %s
            ORDER BY day DESC
            """,
            (project_id, date_from, date_to)
        )
        return [self._row_to_model(r) for r in rows]

    def get_all(self) -> Sequence[TimeLog]:
        rows = self._db.fetch_all(
            f"""
            SELECT {self._COLUMNS} FROM time_logs
            ORDER BY day DESC, id
            """
        )
        return [self._row_to_model(r) for r in rows]

    def create(
        self,
        user_id: int,
        project_id: int,
        day: date,
        hours: float,
        document_id: Optional[int] = None,
        task_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> TimeLog:
        row = self._db.fetch_one(
            f"""
            INSERT INTO time_logs
                (user_id, project_id, document_id, task_id, day, hours, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING {self._COLUMNS}
            """,
            (user_id, project_id, document_id, task_id, day, hours, description)
        )
        return self._row_to_model(row)

    def update(
        self,
        log_id: int,
        hours: Optional[float] = None,
        description: Optional[str] = None,
    ) -> Optional[TimeLog]:
        updates = []
        values = []

        if hours is not None:
            updates.append("hours = %s")
            values.append(hours)
        if description is not None:
            updates.append("description = %s")
            values.append(description)

        if not updates:
            return self.get_by_id(log_id)

        values.append(log_id)
        row = self._db.fetch_one(
            f"UPDATE time_logs SET {', '.join(updates)} WHERE id = %s RETURNING {self._COLUMNS}",
            tuple(values)
        )
        return self._row_to_model(row) if row else None

    def delete(self, log_id: int) -> bool:
        result = self._db.execute("DELETE FROM time_logs WHERE id = %s", (log_id,))
        return result > 0

    def get_hours_by_user_and_project(self, user_id: int, project_id: int, date_from: date, date_to: date) -> float:
        row = self._db.fetch_one(
            "SELECT COALESCE(SUM(hours), 0) FROM time_logs WHERE user_id = %s AND project_id = %s AND day >= %s AND day <= %s",
            (user_id, project_id, date_from, date_to)
        )
        return float(row[0]) if row else 0.0

    def get_hours_by_project(self, project_id: int, date_from: date, date_to: date) -> float:
        row = self._db.fetch_one(
            "SELECT COALESCE(SUM(hours), 0) FROM time_logs WHERE project_id = %s AND day >= %s AND day <= %s",
            (project_id, date_from, date_to)
        )
        return float(row[0]) if row else 0.0

    @staticmethod
    def _row_to_model(row: dict) -> TimeLog:
        return TimeLog(
            id=row["id"],
            user_id=row["user_id"],
            project_id=row["project_id"],
            document_id=row.get("document_id"),
            task_id=row.get("task_id"),
            day=row["day"],
            hours=float(row["hours"]),
            description=row.get("description"),
        )