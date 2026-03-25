from typing import Optional, Sequence
from datetime import date

from db.database import Database
from models.project import Project
from models.enums import ProjectStatus


class ProjectRepository:
    def __init__(self, db: Database):
        self._db = db

    def get_by_id(self, project_id: int) -> Optional[Project]:
        row = self._db.fetch_one(
            """
            SELECT id,
                   code,
                   name,
                   client_name,
                   status,
                   start_date_planned,
                   end_date_planned,
                   start_date_actual,
                   end_date_actual,
                   created_by,
                   created_at
            FROM projects
            WHERE id = %s
            """,
            (project_id,),
        )
        return self._row_to_model(row) if row else None

    def get_all(self) -> Sequence[Project]:
        rows = self._db.fetch_all(
            """
            SELECT id,
                   code,
                   name,
                   client_name,
                   status,
                   start_date_planned,
                   end_date_planned,
                   start_date_actual,
                   end_date_actual,
                   created_by,
                   created_at
            FROM projects
            ORDER BY name
            """
        )
        return [self._row_to_model(r) for r in rows]

    def insert(
        self,
        code: str,
        name: str,
        client_name: str | None,
        status: ProjectStatus,
        start_date_planned: date | None,
        end_date_planned: date | None,
        created_by: int,
    ) -> Project:
        row = self._db.fetch_one(
            """
            INSERT INTO projects (
                code,
                name,
                client_name,
                status,
                start_date_planned,
                end_date_planned,
                created_by
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            RETURNING id,
                      code,
                      name,
                      client_name,
                      status,
                      start_date_planned,
                      end_date_planned,
                      start_date_actual,
                      end_date_actual,
                      created_by,
                      created_at
            """,
            (
                code,
                name,
                client_name,
                status.value,
                start_date_planned,
                end_date_planned,
                created_by,
            ),
        )
        return self._row_to_model(row)

    def update_status(
        self,
        project_id: int,
        status: ProjectStatus,
        start_date_actual: date | None = None,
        end_date_actual: date | None = None,
    ) -> None:
        self._db.execute(
            """
            UPDATE projects
            SET status = %s,
                start_date_actual = COALESCE(%s, start_date_actual),
                end_date_actual   = COALESCE(%s, end_date_actual)
            WHERE id = %s
            """,
            (
                status.value,
                start_date_actual,
                end_date_actual,
                project_id,
            ),
        )

    @staticmethod
    def _row_to_model(row: dict) -> Project:
        return Project(
            id=row["id"],
            code=row["code"],
            name=row["name"],
            client_name=row["client_name"],
            status=ProjectStatus(row["status"]),
            start_date_planned=row["start_date_planned"],
            end_date_planned=row["end_date_planned"],
            start_date_actual=row["start_date_actual"],
            end_date_actual=row["end_date_actual"],
            created_by=row["created_by"],
            created_at=row["created_at"],
        )