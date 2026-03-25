import logging
from datetime import date
from typing import Sequence

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

logger = logging.getLogger(__name__)


class ProjectDashboardService:
    def __init__(
        self,
        project_repo: ProjectRepository,
        task_repo: PlannedTaskRepository,
    ) -> None:
        self._projects = project_repo
        self._tasks = task_repo

    def get_portfolio_today_overview_dto(
        self, target_date: date
    ) -> PortfolioTodayOverviewDTO:
        projects = self._projects.list_all()
        project_overviews: list[ProjectTodayOverviewDTO] = []
        total_at_risk = 0

        for project in projects:
            if project.status in (ProjectStatus.COMPLETED, ProjectStatus.CANCELLED):
                continue

            tasks = self._tasks.get_by_project_id(project.id)
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

    def recalculate_project_metrics(self, project_id: int) -> None:
        logger.info("Recalculated metrics for project %d", project_id)
