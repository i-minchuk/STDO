from typing import Optional, Sequence, Dict, Any
from datetime import date
import json

from db.database import Database
from models.project import Project
from models.enums import ProjectStatus
from repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    _COLUMNS = """
        id, code, name, customer, status, manager_id,
        start_date, end_date_planned, end_date_forecast, end_date_actual, created_at,
        custom_fields, vdr_required, otk_required, crs_deadline_days,
        logistics_delivery_weeks, logistics_complexity
    """

    def __init__(self, db: Database) -> None:
        super().__init__(db, Project, "projects", self._COLUMNS)

    def list_all(self) -> Sequence[Project]:
        return self.list_all(order_by="name")

    def list_all_paginated(self, limit: int = 20, offset: int = 0) -> tuple[Sequence[Project], int]:
        """List all projects with pagination.

        Returns:
            Tuple of (projects list, total count)
        """
        return self._get_paginated(order_by="name", limit=limit, offset=offset)

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
            INSERT INTO {self._table_name} (code, name, customer, status, manager_id,
                                  start_date, end_date_planned, custom_fields,
                                  vdr_required, otk_required, crs_deadline_days,
                                  logistics_delivery_weeks, logistics_complexity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING {self._columns}
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
            f"""
            UPDATE {self._table_name}
            SET status = %s,
                end_date_actual = COALESCE(%s, end_date_actual)
            WHERE id = %s
            """,
            (status.value, end_date_actual, project_id),
        )

    def count_by_status(self, status: ProjectStatus) -> int:
        row = self._db.fetch_one(
            f"SELECT count(*) AS cnt FROM {self._table_name} WHERE status = %s",
            (status.value,),
        )
        return int(row["cnt"]) if row else 0

    def _row_to_model(self, row: dict) -> Project:
        # Override to handle ProjectStatus Enum and JSON custom_fields conversion
        row["status"] = ProjectStatus(row["status"])
        if row.get("custom_fields"):
            row["custom_fields"] = json.loads(row["custom_fields"])
        return super()._row_to_model(row)
