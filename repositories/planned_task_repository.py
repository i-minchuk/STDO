from typing import Optional, Sequence
from datetime import date

from db.database import Database
from models.planned_task import PlannedTask
from models.enums import TaskType, TaskStatus


class PlannedTaskRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = """
        id, project_id, project_code, project_name,
        document_id, document_code, revision_id, revision_index,
        name, task_type, assigned_to, owner_name,
        duration_days_planned, work_hours_planned,
        start_date_planned, end_date_planned,
        start_date_actual, end_date_actual,
        percent_complete, status,
        es, ef, ls, lf, slack, actual_hours
    """

    def get_by_id(self, task_id: int) -> Optional[PlannedTask]:
        row = self._db.fetch_one(
            f"SELECT {self._COLUMNS} FROM planned_tasks WHERE id = %s",
            (task_id,),
        )
        return self._row_to_model(row) if row else None

    def get_by_project_id(self, project_id: int) -> Sequence[PlannedTask]:
        rows = self._db.fetch_all(
            f"""
            SELECT {self._COLUMNS} FROM planned_tasks
            WHERE project_id = %s
            ORDER BY start_date_planned NULLS FIRST, id
            """,
            (project_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def get_by_revision_id(self, revision_id: int) -> Sequence[PlannedTask]:
        rows = self._db.fetch_all(
            f"""
            SELECT {self._COLUMNS} FROM planned_tasks
            WHERE revision_id = %s ORDER BY id
            """,
            (revision_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def insert(
        self,
        project_id: int,
        project_code: str,
        project_name: str,
        document_id: int | None,
        document_code: str | None,
        revision_id: int | None,
        revision_index: str | None,
        name: str,
        task_type: TaskType,
        assigned_to: int | None,
        owner_name: str | None,
        duration_days_planned: int,
        work_hours_planned: float,
        start_date_planned: date | None,
        end_date_planned: date | None,
        status: TaskStatus,
        start_date_actual: date | None = None,
        end_date_actual: date | None = None,
        percent_complete: int = 0,
    ) -> PlannedTask:
        row = self._db.fetch_one(
            f"""
            INSERT INTO planned_tasks (
                project_id, project_code, project_name,
                document_id, document_code, revision_id, revision_index,
                name, task_type, assigned_to, owner_name,
                duration_days_planned, work_hours_planned,
                start_date_planned, end_date_planned,
                start_date_actual, end_date_actual,
                percent_complete, status
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING {self._COLUMNS}
            """,
            (
                project_id, project_code, project_name,
                document_id, document_code, revision_id, revision_index,
                name, task_type.value, assigned_to, owner_name,
                duration_days_planned, work_hours_planned,
                start_date_planned, end_date_planned,
                start_date_actual, end_date_actual,
                percent_complete, status.value,
            ),
        )
        return self._row_to_model(row)

    def update_progress(
        self,
        task_id: int,
        percent_complete: int,
        start_date_actual: date | None,
        end_date_actual: date | None,
        actual_hours: float | None,
        status: TaskStatus,
    ) -> None:
        self._db.execute(
            """
            UPDATE planned_tasks
            SET percent_complete = %s,
                start_date_actual = %s,
                end_date_actual = %s,
                actual_hours = %s,
                status = %s
            WHERE id = %s
            """,
            (percent_complete, start_date_actual, end_date_actual,
             actual_hours, status.value, task_id),
        )

    def update_cpm_fields(self, tasks: Sequence[PlannedTask]) -> None:
        for t in tasks:
            self._db.execute(
                """
                UPDATE planned_tasks
                SET es = %s, ef = %s, ls = %s, lf = %s, slack = %s
                WHERE id = %s
                """,
                (t.es, t.ef, t.ls, t.lf, t.slack, t.id),
            )

    def count_by_project_and_status(
        self, project_id: int, status: TaskStatus
    ) -> int:
        row = self._db.fetch_one(
            "SELECT count(*) AS cnt FROM planned_tasks WHERE project_id = %s AND status = %s",
            (project_id, status.value),
        )
        return int(row["cnt"]) if row else 0

    def count_by_project(self, project_id: int) -> int:
        row = self._db.fetch_one(
            "SELECT count(*) AS cnt FROM planned_tasks WHERE project_id = %s",
            (project_id,),
        )
        return int(row["cnt"]) if row else 0

    @staticmethod
    def _row_to_model(row: dict) -> PlannedTask:
        return PlannedTask(
            id=row["id"],
            project_id=row["project_id"],
            project_code=row["project_code"],
            project_name=row["project_name"],
            document_id=row.get("document_id"),
            document_code=row.get("document_code"),
            revision_id=row.get("revision_id"),
            revision_index=row.get("revision_index"),
            name=row["name"],
            task_type=TaskType(row["task_type"]),
            assigned_to=row.get("assigned_to"),
            owner_name=row.get("owner_name"),
            duration_days_planned=row["duration_days_planned"],
            work_hours_planned=float(row["work_hours_planned"]),
            start_date_planned=row.get("start_date_planned"),
            end_date_planned=row.get("end_date_planned"),
            start_date_actual=row.get("start_date_actual"),
            end_date_actual=row.get("end_date_actual"),
            percent_complete=row["percent_complete"],
            status=TaskStatus(row["status"]),
            es=row.get("es"),
            ef=row.get("ef"),
            ls=row.get("ls"),
            lf=row.get("lf"),
            slack=row.get("slack"),
            actual_hours=float(row["actual_hours"]) if row.get("actual_hours") is not None else None,
        )
