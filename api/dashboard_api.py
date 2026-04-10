from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from core.auth import get_current_user
from core.service_locator import get_locator
from core.authorization import check_project_access
from models.user import User
from models.enums import TaskStatus, ProjectStatus

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/portfolio")
def portfolio(current_user: User = Depends(get_current_user)):
    loc = get_locator()
    projects = loc.project_repo.list_all()
    result = []
    for p in projects:
        tasks = loc.planned_task_repo.get_by_project_id(p.id)
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        spi = round(completed / total, 2) if total > 0 else None
        result.append({
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "status": p.status.value,
            "customer": p.customer,
            "start_date": str(p.start_date) if p.start_date else None,
            "end_date_planned": str(p.end_date_planned) if p.end_date_planned else None,
            "total_tasks": total,
            "completed_tasks": completed,
            "spi": spi,
            "risk_level": "high" if spi and spi < 0.8 else ("medium" if spi and spi < 0.95 else "low"),
        })
    summary = {
        "total": len(projects),
        "active": sum(1 for p in result if p["status"] in ("active", "in_progress")),
        "at_risk": sum(1 for p in result if p["risk_level"] == "high"),
        "completed": sum(1 for p in result if p["status"] == "completed"),
    }
    return {"summary": summary, "projects": result}


@router.get("/project/{project_id}")
def project_health(project_id: int, current_user: User = Depends(get_current_user)):
    # Проверка доступа к проекту
    check_project_access(project_id, current_user)
    
    from datetime import date as date_module
    loc = get_locator()
    project = loc.project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    tasks = loc.planned_task_repo.get_by_project_id(project_id)
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
    critical = [t for t in tasks if t.slack is not None and t.slack == 0]
    today = date_module.today()
    overdue = sum(1 for t in tasks if t.status != TaskStatus.COMPLETED
                  and t.end_date_planned and t.end_date_planned < today)
    spi = round(completed / total, 2) if total > 0 else None
    return {
        "project": {"id": project.id, "name": project.name, "code": project.code},
        "spi": spi,
        "total_tasks": total,
        "completed_tasks": completed,
        "in_progress_tasks": in_progress,
        "critical_tasks": len(critical),
        "overdue_tasks": overdue,
        "risk_level": "high" if spi and spi < 0.8 else ("medium" if spi and spi < 0.95 else "low"),
    }


@router.get("/project/{project_id}/engineers")
def engineer_spi(project_id: int, current_user: User = Depends(get_current_user)):
    # Проверка доступа к проекту
    check_project_access(project_id, current_user)
    
    loc = get_locator()
    tasks = loc.planned_task_repo.get_by_project_id(project_id)
    by_eng = {}
    for t in tasks:
        eng = t.owner_name or "Не назначен"
        if eng not in by_eng:
            by_eng[eng] = {"total": 0, "completed": 0}
        by_eng[eng]["total"] += 1
        if t.status == TaskStatus.COMPLETED:
            by_eng[eng]["completed"] += 1
    return [
        {
            "engineer": eng,
            "total_tasks": data["total"],
            "completed_tasks": data["completed"],
            "spi": round(data["completed"] / data["total"], 2) if data["total"] > 0 else None,
        }
        for eng, data in by_eng.items()
    ]


@router.get("/project/{project_id}/doc-types")
def doc_type_spi(project_id: int, current_user: User = Depends(get_current_user)):
    # Проверка доступа к проекту
    check_project_access(project_id, current_user)
    
    loc = get_locator()
    tasks = loc.planned_task_repo.get_by_project_id(project_id)
    by_type = {}
    for t in tasks:
        dt = getattr(t, 'doc_type', None) or "Прочее"
        if dt not in by_type:
            by_type[dt] = {"total": 0, "completed": 0}
        by_type[dt]["total"] += 1
        if t.status == "completed":
            by_type[dt]["completed"] += 1
    return [
        {
            "doc_type": dt,
            "total_tasks": data["total"],
            "completed_tasks": data["completed"],
            "spi": round(data["completed"] / data["total"], 2) if data["total"] > 0 else None,
        }
        for dt, data in by_type.items()
    ]


class ProjectMetricsDTO(BaseModel):
    project_id: int
    calculated_at: Optional[datetime] = None
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    not_started_tasks: int
    spi: float
    cpi: float
    risk_level: str
    critical_tasks: int
    overdue_tasks: int
    total_planned_hours: Optional[float] = None
    completed_hours: Optional[float] = None


@router.get("/project/{project_id}/metrics", response_model=ProjectMetricsDTO)
def get_project_metrics(project_id: int, current_user: User = Depends(get_current_user)):
    """Получить последние сохранённые метрики проекта."""
    check_project_access(project_id, current_user)
    
    loc = get_locator()
    project = loc.project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    # Пробуем получить метрики из БД
    metrics = loc.project_dashboard.get_latest_metrics(project_id)
    
    if metrics is None:
        # Если метрик нет - пересчитываем
        metrics = loc.project_dashboard.recalculate_project_metrics(project_id)
        # Пересчитанные метрики не имеют calculated_at
        metrics["calculated_at"] = None
    
    return ProjectMetricsDTO(
        project_id=project_id,
        calculated_at=metrics.get("calculated_at"),
        total_tasks=metrics.get("total", 0),
        completed_tasks=metrics.get("completed", 0),
        in_progress_tasks=metrics.get("in_progress", 0),
        blocked_tasks=metrics.get("blocked", 0),
        not_started_tasks=metrics.get("not_started", 0),
        spi=metrics.get("spi", 1.0),
        cpi=metrics.get("cpi", 1.0),
        risk_level=metrics.get("risk_level", "low"),
        critical_tasks=metrics.get("critical_tasks", 0),
        overdue_tasks=metrics.get("overdue_tasks", 0),
        total_planned_hours=metrics.get("total_planned_hours"),
        completed_hours=metrics.get("completed_hours"),
    )


@router.post("/project/{project_id}/metrics/recalculate")
def recalculate_project_metrics(project_id: int, current_user: User = Depends(get_current_user)):
    """Принудительно пересчитать метрики проекта и сохранить в БД."""
    check_project_access(project_id, current_user)
    
    loc = get_locator()
    project = loc.project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    # Пересчитываем метрики (с сохранением в БД)
    metrics = loc.project_dashboard.recalculate_project_metrics(project_id)
    
    return {
        "status": "ok",
        "project_id": project_id,
        "metrics": metrics,
    }
