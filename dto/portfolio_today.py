from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from .common import ProjectShortDTO


class ProjectHealthDTO(BaseModel):
    percent_complete: float
    spi: float
    cpi: float
    schedule_risk_level: str
    cost_risk_level: str


class ProjectTodayWorkloadDTO(BaseModel):
    planned_hours_today: float
    logged_hours_today: float
    critical_tasks_today: int
    review_tasks_today: int
    approval_tasks_today: int


class ProjectTodayOverviewDTO(BaseModel):
    project: ProjectShortDTO
    manager: Optional[str] = None
    summary_label: Optional[str] = None
    start_date: Optional[date] = None
    end_date_planned: Optional[date] = None
    end_date_forecast: Optional[date] = None
    end_date_actual: Optional[date] = None
    health: ProjectHealthDTO
    today_workload: ProjectTodayWorkloadDTO


class PortfolioSummaryDTO(BaseModel):
    projects_total: int
    projects_at_risk: int
    avg_spi: float
    avg_cpi: float
    total_capacity_hours_today: float
    total_planned_hours_today: float
    total_logged_hours_today: float


class PortfolioTodayOverviewDTO(BaseModel):
    date: date
    portfolio_summary: PortfolioSummaryDTO
    projects: List[ProjectTodayOverviewDTO]