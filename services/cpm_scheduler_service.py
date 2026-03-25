# services/cpm_scheduler_service.py
from collections import defaultdict, deque
from typing import Dict, List, Tuple

from db.database import Database
from repositories.planned_task_repository import PlannedTaskRepository
from repositories.task_dependency_repository import TaskDependencyRepository
from models.planned_task import PlannedTask
from models.task_dependency import TaskDependency


class CPMSchedulerService:
    def __init__(
        self,
        db: Database,
        task_repo: PlannedTaskRepository,
        dep_repo: TaskDependencyRepository,
    ):
        self._db = db
        self._tasks = task_repo
        self._deps = dep_repo

    def recalculate_project_schedule(self, project_id: int) -> list[int]:
        tasks = self._tasks.get_by_project(project_id)
        deps = self._deps.get_by_project(project_id)
        if not tasks:
            return []

        graph, indegree, reverse_graph, duration = self._build_graph(tasks, deps)
        es, ef, project_duration = self._forward_pass(graph, indegree, duration)
        ls, lf = self._backward_pass(graph, reverse_graph, duration, project_duration)

        critical_ids: list[int] = []
        for t in tasks:
            t.es = es[t.id]
            t.ef = ef[t.id]
            t.ls = ls[t.id]
            t.lf = lf[t.id]
            t.slack = t.ls - t.es
            if t.slack == 0:
                critical_ids.append(t.id)

        self._tasks.update_cpm_fields(tasks)
        return critical_ids

    # _build_graph, _forward_pass, _backward_pass — как в детальной версии выше