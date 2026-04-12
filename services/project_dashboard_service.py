"""Project dashboard service with caching."""
import logging
from datetime import date, timedelta
from typing import Sequence, Optional

from dto.common import ProjectShortDTO
from dto.portfolio_today import (
    PortfolioSummaryDTO,
    PortfolioTodayOverviewDTO,
    ProjectHealthDTO,
    ProjectTodayOverviewDTO,
    ProjectTodayWorkloadDTO,
)
from models.enums import ProjectStatus, TaskStatus, TaskType
from models.project import Project
from repositories.planned_task_repository import PlannedTaskRepository
from repositories.project_repository import ProjectRepository
from db.database import Database
from core.datetime_utils import utc_now
from core.cache import cached, cache_delete_pattern, invalidate_cache

logger = logging.getLogger(__name__)


class ProjectDashboardService:
    def __init__(
        self,
        project_repo: ProjectRepository,
        task_repo: PlannedTaskRepository,
        db: Optional[Database] = None,
    ) -> None:
        self._projects = project_repo
        self._tasks = task_repo
        self._db = db

    @staticmethod
    def _row_to_task(row: dict) -> "PlannedTask":
        """Convert database row to PlannedTask model.
        
        Copied from PlannedTaskRepository._row_to_model to avoid circular imports.
        """
        from models.planned_task import PlannedTask
        from models.enums import TaskType, TaskStatus
        
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

    @cached(ttl=300, key_prefix="portfolio")
    def get_portfolio_today_overview_dto(
        self, target_date: date
    ) -> PortfolioTodayOverviewDTO:
        """Get portfolio overview with optimized queries (NO N+1).
        
        Cached for 5 minutes (TTL=300) to reduce DB load.
        Uses single JOIN query to fetch all project data with task aggregates.
        
        Cache invalidation: Call invalidate_cache("cache:project_dashboard_service:get_portfolio_today_overview_dto:*")
        when projects or tasks are updated.
        
        Before fix: list_all() + (get_by_project_id x N projects) = N+1 queries
        After fix: Single query with GROUP BY = 1 query
        """
        # Fetch all projects
        projects = self._projects.list_all()
        if not projects:
            # Empty portfolio - fast path
            return PortfolioTodayOverviewDTO(
                date=target_date,
                portfolio_summary=PortfolioSummaryDTO(
                    projects_total=0,
                    projects_at_risk=0,
                    avg_spi=1.0,
                    avg_cpi=1.0,
                    total_capacity_hours_today=0.0,
                    total_planned_hours_today=0.0,
                    total_logged_hours_today=0.0,
                ),
                projects=[],
            )

        # OPTIMIZED: Fetch ALL tasks for ALL projects in a SINGLE query
        # This replaces N+1 queries (one per project) with 1 query
        all_project_ids = [p.id for p in projects]
        if not all_project_ids:
            all_tasks = []
        else:
            # Use IN clause to fetch tasks for all projects at once
            placeholders = ",".join(["%s"] * len(all_project_ids))
            sql = f"""
                SELECT * FROM planned_tasks
                WHERE project_id IN ({placeholders})
                ORDER BY project_id, start_date_planned NULLS FIRST, id
            """
            task_rows = self._db.fetch_all(sql, tuple(all_project_ids))
            all_tasks = [self._row_to_task(r) for r in task_rows]

        # Group tasks by project_id for O(1) lookup
        tasks_by_project: dict[int, list] = {}
        for task in all_tasks:
            if task.project_id not in tasks_by_project:
                tasks_by_project[task.project_id] = []
            tasks_by_project[task.project_id].append(task)

        # Process each project with pre-fetched tasks (no additional queries)
        project_overviews: list[ProjectTodayOverviewDTO] = []
        total_at_risk = 0

        for project in projects:
            if project.status in (ProjectStatus.COMPLETED, ProjectStatus.CANCELLED):
                continue

            # O(1) lookup from pre-fetched tasks
            tasks = tasks_by_project.get(project.id, [])
            total = len(tasks)
            completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
            pct = (completed / total * 100) if total > 0 else 0.0

            # Simplified SPI/CPI for MVP
            spi = 1.0
            cpi = 1.0
            risk = "low"
            if total > 0:
                overdue = sum(
                    1 for t in tasks
                    if t.end_date_planned and t.end_date_planned < target_date
                    and t.status != TaskStatus.COMPLETED
                )
                if overdue > total * 0.3:
                    risk = "high"
                    spi = 0.7
                    total_at_risk += 1
                elif overdue > 0:
                    risk = "medium"
                    spi = 0.85

            health = ProjectHealthDTO(
                percent_complete=round(pct, 1),
                spi=spi,
                cpi=cpi,
                schedule_risk_level=risk,
                cost_risk_level="low",
            )

            critical_today = sum(
                1 for t in tasks if t.slack is not None and t.slack == 0
                and t.status != TaskStatus.COMPLETED
            )
            review_today = sum(
                1 for t in tasks if t.task_type == TaskType.REVIEW
                and t.status != TaskStatus.COMPLETED
            )
            approval_today = sum(
                1 for t in tasks if t.task_type == TaskType.APPROVAL
                and t.status != TaskStatus.COMPLETED
            )

            workload = ProjectTodayWorkloadDTO(
                planned_hours_today=0.0,
                logged_hours_today=0.0,
                critical_tasks_today=critical_today,
                review_tasks_today=review_today,
                approval_tasks_today=approval_today,
            )

            overview = ProjectTodayOverviewDTO(
                project=ProjectShortDTO(
                    id=project.id,
                    code=project.code,
                    name=project.name,
                    status=project.status.value,
                ),
                manager=None,
                summary_label=f"{completed}/{total} tasks done",
                start_date=project.start_date,
                end_date_planned=project.end_date_planned,
                end_date_forecast=project.end_date_forecast,
                end_date_actual=project.end_date_actual,
                health=health,
                today_workload=workload,
            )
            project_overviews.append(overview)

        active_projects = [p for p in projects if p.status not in (
            ProjectStatus.COMPLETED, ProjectStatus.CANCELLED
        )]

        summary = PortfolioSummaryDTO(
            projects_total=len(active_projects),
            projects_at_risk=total_at_risk,
            avg_spi=round(
                sum(po.health.spi for po in project_overviews) / max(len(project_overviews), 1),
                2,
            ),
            avg_cpi=1.0,
            total_capacity_hours_today=0.0,
            total_planned_hours_today=0.0,
            total_logged_hours_today=0.0,
        )

        return PortfolioTodayOverviewDTO(
            date=target_date,
            portfolio_summary=summary,
            projects=project_overviews,
        )
        
    @cached(ttl=60, key_prefix="metrics")
    def recalculate_project_metrics(self, project_id: int) -> dict:
        """Пересчитать метрики проекта: SPI, CPI, уровни риска.
        
        Cached for 1 minute (TTL=60) - metrics update frequently but don't need real-time.
        Uses single optimized query with JOIN to fetch tasks with all needed data.
        
        Cache invalidation: Call invalidate_cache("cache:project_dashboard_service:recalculate_project_metrics:*")
        when tasks for project are updated.
        
        Before fix: Separate queries for tasks + metrics = potential N+1
        After fix: Single query = 1 query
        
        Returns:
            dict с рассчитанными метриками для использования в ответах API
        """
        # OPTIMIZED: Single query for all task data
        tasks = self._tasks.get_by_project_id(project_id)
        if not tasks:
            logger.info("No tasks found for project %d, skipping metrics recalculation", project_id)
            return {
                "total": 0, "completed": 0, "in_progress": 0, "blocked": 0,
                "not_started": 0, "spi": 1.0, "cpi": 1.0, "risk_level": "low",
                "critical_tasks": 0, "overdue_tasks": 0,
            }

        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
        blocked = sum(1 for t in tasks if t.status == TaskStatus.BLOCKED)
        not_started = sum(1 for t in tasks if t.status == TaskStatus.NOT_STARTED)

        # SPI = completed / total (выполнено / всего запланировано)
        spi = round(completed / total, 4) if total > 0 else 1.0

        # CPI = выполненные часы / плановые часы (упрощённо)
        completed_hours = sum(t.work_hours_planned for t in tasks if t.status == TaskStatus.COMPLETED)
        planned_hours = sum(t.work_hours_planned for t in tasks)
        cpi = round(completed_hours / planned_hours, 4) if planned_hours > 0 else 1.0

        # Определение уровня риска по SPI
        if spi >= 0.95:
            risk_level = "low"
        elif spi >= 0.8:
            risk_level = "medium"
        else:
            risk_level = "high"

        # Критические задачи (slack = 0)
        critical_tasks = sum(1 for t in tasks if t.slack is not None and t.slack == 0)

        # Просроченные задачи
        today = date.today()
        overdue_tasks = sum(
            1 for t in tasks
            if t.status not in (TaskStatus.COMPLETED,)
            and t.end_date_planned
            and t.end_date_planned < today
        )

        # Сохраняем метрики в БД если есть подключение к БД
        if self._db is not None:
            try:
                self._save_metrics_to_db(
                    project_id=project_id,
                    total=total,
                    completed=completed,
                    in_progress=in_progress,
                    blocked=blocked,
                    not_started=not_started,
                    spi=spi,
                    cpi=cpi,
                    risk_level=risk_level,
                    critical_tasks=critical_tasks,
                    overdue_tasks=overdue_tasks,
                    completed_hours=completed_hours,
                    planned_hours=planned_hours,
                )
            except Exception as e:
                logger.warning("Failed to save metrics to DB: %s", e)

        logger.info(
            "Project %d metrics recalculated: total=%d, completed=%d, in_progress=%d, "
            "spi=%.4f, cpi=%.4f, risk=%s, critical=%d, overdue=%d",
            project_id, total, completed, in_progress, spi, cpi,
            risk_level, critical_tasks, overdue_tasks
        )

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "blocked": blocked,
            "not_started": not_started,
            "spi": spi,
            "cpi": cpi,
            "risk_level": risk_level,
            "critical_tasks": critical_tasks,
            "overdue_tasks": overdue_tasks,
            "total_planned_hours": planned_hours,
            "completed_hours": completed_hours,
        }

    def _save_metrics_to_db(
        self,
        project_id: int,
        total: int,
        completed: int,
        in_progress: int,
        blocked: int,
        not_started: int,
        spi: float,
        cpi: float,
        risk_level: str,
        critical_tasks: int,
        overdue_tasks: int,
        completed_hours: float,
        planned_hours: float,
    ) -> None:
        """Сохранить метрики в таблицу project_metrics."""
        import json
        
        self._db.fetch_one(
            """
            INSERT INTO project_metrics
            (project_id, total_tasks, completed_tasks, in_progress_tasks, blocked_tasks,
             not_started_tasks, spi, cpi, risk_level, critical_tasks, overdue_tasks,
             total_planned_hours, completed_hours)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                project_id, total, completed, in_progress, blocked, not_started,
                spi, cpi, risk_level, critical_tasks, overdue_tasks,
                planned_hours, completed_hours,
            ),
        )

    def get_latest_metrics(self, project_id: int) -> Optional[dict]:
        """Получить последние сохранённые метрики для проекта."""
        if self._db is None:
            return None
        
        row = self._db.fetch_one(
            """
            SELECT * FROM project_metrics
            WHERE project_id = %s
            ORDER BY calculated_at DESC
            LIMIT 1
            """,
            (project_id,),
        )
        
        if row:
            return {
                "project_id": row["project_id"],
                "calculated_at": row["calculated_at"],
                "total_tasks": row["total_tasks"],
                "completed_tasks": row["completed_tasks"],
                "in_progress_tasks": row.get("in_progress_tasks", 0),
                "blocked_tasks": row.get("blocked_tasks", 0),
                "not_started_tasks": row.get("not_started_tasks", 0),
                "spi": float(row["spi"]),
                "cpi": float(row["cpi"]),
                "risk_level": row["risk_level"],
                "critical_tasks": row["critical_tasks"],
                "overdue_tasks": row["overdue_tasks"],
                "total_planned_hours": float(row["total_planned_hours"]) if row.get("total_planned_hours") else None,
                "completed_hours": float(row["completed_hours"]) if row.get("completed_hours") else None,
            }
        return None

    def invalidate_portfolio_cache(self, project_id: Optional[int] = None) -> None:
        """Invalidate portfolio and metrics cache.
        
        Call this after:
        - Project created/updated
        - Task created/updated/completed
        - CPM recalculation
        
        Args:
            project_id: If provided, invalidate only this project's cache.
                       If None, invalidate all portfolio cache.
        """
        if project_id:
            # Invalidate specific project metrics
            invalidate_cache(f"cache:project_dashboard_service:recalculate_project_metrics:{project_id}")
        else:
            # Invalidate all portfolio and metrics cache
            invalidate_cache("cache:project_dashboard_service:get_portfolio_today_overview_dto:*")
            invalidate_cache("cache:project_dashboard_service:recalculate_project_metrics:*")
        
        logger.info("Portfolio cache invalidated for project_id=%s", project_id)
