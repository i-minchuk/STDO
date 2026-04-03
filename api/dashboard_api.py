from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user
from core.service_locator import get_locator
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
