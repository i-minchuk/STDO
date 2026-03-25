from typing import Optional, Sequence
from datetime import date

from db.database import Database
from models.planned_task import PlannedTask
from models.enums import TaskType, TaskStatus


class PlannedTaskRepository:
    def __init__(self, db: Database):
        self._db = db

    def get_by_id(self, task_id: int) -> Optional[PlannedTask]:
        row = self._db.fetch_one(
            """
            SELECT id,
                   project_id,
                   project_code,
                   project_name,
                   document_id,
                   document_code,
                   revision_id,
                   revision_index,
                   name,
                   task_type,
                   assigned_to,
                   owner_name,
                   duration_days_planned,
                   work_hours_planned,
                   start_date_planned,
                   end_date_planned,
                   start_date_actual,
                   end_date_actual,
                   percent_complete,
                   status,
                   es,
                   ef,
                   ls,
                   lf,
                   slack,
                   actual_hours
            FROM planned_tasks
            WHERE id = %s
            """,
            (task_id,),
        )
        return self._row_to_model(row) if row else None

    def get_by_project_id(self, project_id: int) -> Sequence[PlannedTask]:
        rows = self._db.fetch_all(
            """
            SELECT id,
                   project_id,
                   project_code,
                   project_name,
                   document_id,
                   document_code,
                   revision_id,
                   revision_index,
                   name,
                   task_type,
                   assigned_to,
                   owner_name,
                   duration_days_planned,
                   work_hours_planned,
                   start_date_planned,
                   end_date_planned,
                   start_date_actual,
                   end_date_actual,
                   percent_complete,
                   status,
                   es,
                   ef,
                   ls,
                   lf,
                   slack,
                   actual_hours
            FROM planned_tasks
            WHERE project_id = %s
            ORDER BY start_date_planned NULLS FIRST, id
            """,
            (project_id,),
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
        start_date_actual: date | None,
        end_date_actual: date | None,
        percent_complete: int,
        status: TaskStatus,
        es: int | None = None,
        ef: int | None = None,
        ls: int | None = None,
        lf: int | None = None,
        slack: int | None = None,
        actual_hours: float | None = None,
    ) -> PlannedTask:
        row = self._db.fetch_one(
            """
            INSERT INTO planned_tasks (
                project_id,
                project_code,
                project_name,
                document_id,
                document_code,
                revision_id,
                revision_index,
                name,
                task_type,
                assigned_to,
                owner_name,
                duration_days_planned,
                work_hours_planned,
                start_date_planned,
                end_date_planned,
                start_date_actual,
                end_date_actual,
                percent_complete,
                status,
                es,
                ef,
                ls,
                lf,
                slack,
                actual_hours
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id,
                      project_id,
                      project_code,
                      project_name,
                      document_id,
                      document_code,
                      revision_id,
                      revision_index,
                      name,
                      task_type,
                      assigned_to,
                      owner_name,
                      duration_days_planned,
                      work_hours_planned,
                      start_date_planned,
                      end_date_planned,
                      start_date_actual,
                      end_date_actual,
                      percent_complete,
                      status,
                      es,
                      ef,
                      ls,
                      lf,
                      slack,
                      actual_hours
            """,
            (
                project_id,
                project_code,
                project_name,
                document_id,
                document_code,
                revision_id,
                revision_index,
                name,
                task_type.value,
                assigned_to,
                owner_name,
                duration_days_planned,
                work_hours_planned,
                start_date_planned,
                end_date_planned,
                start_date_actual,
                end_date_actual,
                percent_complete,
                status.value,
                es,
                ef,
                ls,
                lf,
                slack,
                actual_hours,
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
            (
                percent_complete,
                start_date_actual,
                end_date_actual,
                actual_hours,
                status.value,
                task_id,
            ),
        )

    @staticmethod
    def _row_to_model(row: dict) -> PlannedTask:
        return PlannedTask(
            id=row["id"],
            project_id=row["project_id"],
            project_code=row["project_code"],
            project_name=row["project_name"],
            document_id=row["document_id"],
            document_code=row["document_code"],
            revision_id=row["revision_id"],
            revision_index=row["revision_index"],
            name=row["name"],
            task_type=TaskType(row["task_type"]),
            assigned_to=row["assigned_to"],
            owner_name=row["owner_name"],
            duration_days_planned=row["duration_days_planned"],
            work_hours_planned=row["work_hours_planned"],
            start_date_planned=row["start_date_planned"],
            end_date_planned=row["end_date_planned"],
            start_date_actual=row["start_date_actual"],
            end_date_actual=row["end_date_actual"],
            percent_complete=row["percent_complete"],
            status=TaskStatus(row["status"]),
            es=row["es"],
            ef=row["ef"],
            ls=row["ls"],
            lf=row["lf"],
            slack=row["slack"],
            actual_hours=row["actual_hours"],
        )