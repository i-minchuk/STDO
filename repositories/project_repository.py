from typing import Optional, Sequence
from datetime import date

from db.database import Database
from models.project import Project
from models.enums import ProjectStatus


class ProjectRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = """
        id, code, name, customer, status, manager_id,
        start_date, end_date_planned, end_date_forecast, end_date_actual, created_at
    """

    def get_by_id(self, project_id: int) -> Optional[Project]:
        row = self._db.fetch_one(
            f"SELECT {self._COLUMNS} FROM projects WHERE id = %s",
            (project_id,),
        )
        return self._row_to_model(row) if row else None

    def list_all(self) -> Sequence[Project]:
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM projects ORDER BY name"
        )
        return [self._row_to_model(r) for r in rows]

    def insert(
        self,
        code: str,
        name: str,
        customer: str | None,
        status: ProjectStatus,
        manager_id: int | None,
        start_date: date | None,
        end_date_planned: date | None,
    ) -> Project:
        row = self._db.fetch_one(
            f"""
            INSERT INTO projects (code, name, customer, status, manager_id,
                                  start_date, end_date_planned)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING {self._COLUMNS}
            """,
            (code, name, customer, status.value, manager_id,
             start_date, end_date_planned),
        )
        return self._row_to_model(row)

    def update_status(
        self,
        project_id: int,
        status: ProjectStatus,
        end_date_actual: date | None = None,
    ) -> None:
        self._db.execute(
            """
            UPDATE projects
            SET status = %s,
                end_date_actual = COALESCE(%s, end_date_actual)
            WHERE id = %s
            """,
            (status.value, end_date_actual, project_id),
        )

    def count_by_status(self, status: ProjectStatus) -> int:
        row = self._db.fetch_one(
            "SELECT count(*) AS cnt FROM projects WHERE status = %s",
            (status.value,),
        )
        return int(row["cnt"]) if row else 0

    @staticmethod
    def _row_to_model(row: dict) -> Project:
        return Project(
            id=row["id"],
            code=row["code"],
            name=row["name"],
            customer=row.get("customer"),
            status=ProjectStatus(row["status"]),
            manager_id=row.get("manager_id"),
            start_date=row.get("start_date"),
            end_date_planned=row.get("end_date_planned"),
            end_date_forecast=row.get("end_date_forecast"),
            end_date_actual=row.get("end_date_actual"),
            created_at=row["created_at"],
        )
