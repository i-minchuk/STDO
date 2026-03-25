from typing import Optional, Sequence

from db.database import Database
from models.task_dependency import TaskDependency


class TaskDependencyRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = """
        id, project_id, predecessor_task_id, successor_task_id,
        dependency_type, lag_days
    """

    def get_by_id(self, dep_id: int) -> Optional[TaskDependency]:
        row = self._db.fetch_one(
            f"SELECT {self._COLUMNS} FROM task_dependencies WHERE id = %s",
            (dep_id,),
        )
        return self._row_to_model(row) if row else None

    def get_for_project(self, project_id: int) -> Sequence[TaskDependency]:
        rows = self._db.fetch_all(
            f"""
            SELECT {self._COLUMNS} FROM task_dependencies
            WHERE project_id = %s
            ORDER BY predecessor_task_id, successor_task_id
            """,
            (project_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def get_for_task(self, task_id: int) -> Sequence[TaskDependency]:
        rows = self._db.fetch_all(
            f"""
            SELECT {self._COLUMNS} FROM task_dependencies
            WHERE predecessor_task_id = %s OR successor_task_id = %s
            ORDER BY id
            """,
            (task_id, task_id),
        )
        return [self._row_to_model(r) for r in rows]

    def insert(
        self,
        project_id: int,
        predecessor_task_id: int,
        successor_task_id: int,
        dependency_type: str = "FS",
        lag_days: int = 0,
    ) -> TaskDependency:
        row = self._db.fetch_one(
            f"""
            INSERT INTO task_dependencies (
                project_id, predecessor_task_id, successor_task_id,
                dependency_type, lag_days
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING {self._COLUMNS}
            """,
            (project_id, predecessor_task_id, successor_task_id,
             dependency_type, lag_days),
        )
        return self._row_to_model(row)

    def delete_for_task(self, task_id: int) -> None:
        self._db.execute(
            """
            DELETE FROM task_dependencies
            WHERE predecessor_task_id = %s OR successor_task_id = %s
            """,
            (task_id, task_id),
        )

    def delete_between(
        self, predecessor_task_id: int, successor_task_id: int
    ) -> None:
        self._db.execute(
            """
            DELETE FROM task_dependencies
            WHERE predecessor_task_id = %s AND successor_task_id = %s
            """,
            (predecessor_task_id, successor_task_id),
        )

    @staticmethod
    def _row_to_model(row: dict) -> TaskDependency:
        return TaskDependency(
            id=row["id"],
            project_id=row["project_id"],
            predecessor_task_id=row["predecessor_task_id"],
            successor_task_id=row["successor_task_id"],
            dependency_type=row["dependency_type"],
            lag_days=row["lag_days"],
        )
