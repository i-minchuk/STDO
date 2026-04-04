from typing import Optional, Sequence, Dict, Any
from datetime import date
import json

from db.database import Database
from models.project import Project
from models.enums import ProjectStatus


class ProjectRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = """
        id, code, name, customer, status, manager_id,
        start_date, end_date_planned, end_date_forecast, end_date_actual, created_at,
        custom_fields, vdr_required, otk_required, crs_deadline_days,
        logistics_delivery_weeks, logistics_complexity
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

    def list_all_paginated(self, limit: int = 20, offset: int = 0) -> tuple[Sequence[Project], int]:
        """List all projects with pagination.

        Returns:
            Tuple of (projects list, total count)
        """
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM projects ORDER BY name LIMIT %s OFFSET %s",
            (limit, offset),
        )
        projects = [self._row_to_model(r) for r in rows]

        # Get total count
        total_row = self._db.fetch_one("SELECT count(*) AS cnt FROM projects")
        total = int(total_row["cnt"]) if total_row else 0

        return projects, total

    def insert(
        self,
        code: str,
        name: str,
        customer: str | None,
        status: ProjectStatus,
        manager_id: int | None,
        start_date: date | None,
        end_date_planned: date | None,
        custom_fields: Optional[Dict[str, Any]] = None,
        vdr_required: bool = False,
        otk_required: bool = False,
        crs_deadline_days: int = 3,
        logistics_delivery_weeks: int = 2,
        logistics_complexity: str = "normal",
    ) -> Project:
        row = self._db.fetch_one(
            f"""
            INSERT INTO projects (code, name, customer, status, manager_id,
                                  start_date, end_date_planned, custom_fields,
                                  vdr_required, otk_required, crs_deadline_days,
                                  logistics_delivery_weeks, logistics_complexity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING {self._COLUMNS}
            """,
            (code, name, customer, status.value, manager_id,
             start_date, end_date_planned, json.dumps(custom_fields) if custom_fields else None,
             vdr_required, otk_required, crs_deadline_days,
             logistics_delivery_weeks, logistics_complexity),
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
            custom_fields=json.loads(row["custom_fields"]) if row.get("custom_fields") else None,
            vdr_required=bool(row.get("vdr_required", False)),
            otk_required=bool(row.get("otk_required", False)),
            crs_deadline_days=int(row.get("crs_deadline_days", 3)),
            logistics_delivery_weeks=int(row.get("logistics_delivery_weeks", 2)),
            logistics_complexity=row.get("logistics_complexity", "normal"),
        )
