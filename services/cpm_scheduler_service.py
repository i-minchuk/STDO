import logging
from collections import defaultdict, deque

from db.database import Database
from models.planned_task import PlannedTask
from models.task_dependency import TaskDependency
from repositories.planned_task_repository import PlannedTaskRepository
from repositories.task_dependency_repository import TaskDependencyRepository

logger = logging.getLogger(__name__)


class CPMSchedulerService:
    """Critical Path Method scheduler — forward/backward pass with FS dependencies."""

    def __init__(
        self,
        db: Database,
        task_repo: PlannedTaskRepository,
        dep_repo: TaskDependencyRepository,
    ) -> None:
        self._db = db
        self._tasks = task_repo
        self._deps = dep_repo

    def recalculate_project_schedule(self, project_id: int) -> list[int]:
        tasks = self._tasks.get_by_project_id(project_id)
        deps = self._deps.get_for_project(project_id)
        if not tasks:
            return []

        task_map: dict[int, PlannedTask] = {t.id: t for t in tasks}
        duration: dict[int, int] = {t.id: t.duration_days_planned for t in tasks}

        # Build adjacency lists and in-degree counts
        successors: dict[int, list[int]] = defaultdict(list)
        predecessors: dict[int, list[int]] = defaultdict(list)
        lag: dict[tuple[int, int], int] = {}
        in_degree: dict[int, int] = {t.id: 0 for t in tasks}

        for dep in deps:
            if dep.predecessor_task_id in task_map and dep.successor_task_id in task_map:
                successors[dep.predecessor_task_id].append(dep.successor_task_id)
                predecessors[dep.successor_task_id].append(dep.predecessor_task_id)
                in_degree[dep.successor_task_id] = in_degree.get(dep.successor_task_id, 0) + 1
                lag[(dep.predecessor_task_id, dep.successor_task_id)] = dep.lag_days

        # Forward pass (topological order via Kahn's algorithm)
        es: dict[int, int] = {}
        ef: dict[int, int] = {}
        queue: deque[int] = deque()

        for tid in task_map:
            if in_degree.get(tid, 0) == 0:
                es[tid] = 0
                ef[tid] = duration[tid]
                queue.append(tid)

        while queue:
            current = queue.popleft()
            for succ in successors[current]:
                candidate_es = ef[current] + lag.get((current, succ), 0)
                if succ not in es or candidate_es > es[succ]:
                    es[succ] = candidate_es
                    ef[succ] = candidate_es + duration[succ]
                in_degree[succ] -= 1
                if in_degree[succ] == 0:
                    queue.append(succ)

        if not ef:
            return []

        project_duration = max(ef.values())

        # Backward pass
        ls: dict[int, int] = {}
        lf: dict[int, int] = {}
        out_degree: dict[int, int] = {t.id: len(successors[t.id]) for t in tasks}

        queue = deque()
        for tid in task_map:
            if out_degree.get(tid, 0) == 0:
                lf[tid] = project_duration
                ls[tid] = project_duration - duration[tid]
                queue.append(tid)

        while queue:
            current = queue.popleft()
            for pred_id in predecessors[current]:
                candidate_lf = ls[current] - lag.get((pred_id, current), 0)
                if pred_id not in lf or candidate_lf < lf[pred_id]:
                    lf[pred_id] = candidate_lf
                    ls[pred_id] = candidate_lf - duration[pred_id]
                out_degree[pred_id] -= 1
                if out_degree[pred_id] == 0:
                    queue.append(pred_id)

        # Update task objects and identify critical path
        critical_ids: list[int] = []
        for t in tasks:
            t.es = es.get(t.id)
            t.ef = ef.get(t.id)
            t.ls = ls.get(t.id)
            t.lf = lf.get(t.id)
            if t.es is not None and t.ls is not None:
                t.slack = t.ls - t.es
                if t.slack == 0:
                    critical_ids.append(t.id)
            else:
                t.slack = None

        with self._db.transaction():
            self._tasks.update_cpm_fields(tasks)

        logger.info(
            "CPM recalculated for project %d: %d tasks, %d critical",
            project_id, len(tasks), len(critical_ids),
        )
        return critical_ids
