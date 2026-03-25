from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from core.service_locator import ServiceLocator, get_locator
from dto.common import ProjectShortDTO
from dto.portfolio_today import PortfolioTodayOverviewDTO

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectShortDTO])
def list_projects(locator: ServiceLocator = Depends(get_locator)):
    projects = locator.project_repo.list_all()
    return [
        ProjectShortDTO(
            id=p.id, code=p.code, name=p.name, status=p.status.value,
        )
        for p in projects
    ]


@router.get("/portfolio/today", response_model=PortfolioTodayOverviewDTO)
def get_portfolio_today(locator: ServiceLocator = Depends(get_locator)):
    today = date.today()
    return locator.project_dashboard.get_portfolio_today_overview_dto(today)
