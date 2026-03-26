from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.auth import get_current_user
from core.service_locator import get_locator
from models.user import User

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class StatusUpdate(BaseModel):
    status: str

class TimeLog(BaseModel):
    minutes: int


@router.get("/today")
def today_tasks(current_user: User = Depends(get_current_user)):
    loc = get_locator()
    tasks = loc.planned_task_repo.get_all()
    today = date.today()
    result = []
    for t in tasks:
        if t.status in ("completed",):
            continue
        if t.planned_start and t.planned_start <= today:
            result.append(_task_to_dict(t))
    return result


@router.get("/project/{project_id}")
def project_tasks(project_id: int, current_user: User = Depends(get_current_user)):
    loc = get_locator()
    tasks = loc.planned_task_repo.get_by_project_id(project_id)
    return [_task_to_dict(t) for t in tasks]


@router.get("/{task_id}")
def get_task(task_id: int, current_user: User = Depends(get_current_user)):
    loc = get_locator()
    task = loc.planned_task_repo.get_by_id(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return _task_to_dict(task)


@router.put("/{task_id}/status")
def update_status(task_id: int, body: StatusUpdate, current_user: User = Depends(get_current_user)):
    loc = get_locator()
    task = loc.planned_task_repo.get_by_id(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    task.status = body.status
    return {"ok": True, "status": body.status}


@router.put("/{task_id}/log-time")
def log_time(task_id: int, body: TimeLog, current_user: User = Depends(get_current_user)):
    loc = get_locator()
    task = loc.planned_task_repo.get_by_id(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return {"ok": True, "minutes_logged": body.minutes}


def _task_to_dict(t) -> dict:
    return {
        "id": t.id, "project_id": t.project_id,
        "document_id": t.document_id,
        "task_type": t.task_type if hasattr(t, 'task_type') else None,
        "title": getattr(t, 'title', None) or getattr(t, 'document_code', ''),
        "status": t.status,
        "planned_start": str(t.planned_start) if t.planned_start else None,
        "planned_finish": str(t.planned_finish) if t.planned_finish else None,
        "planned_hours": t.planned_hours,
        "actual_hours": getattr(t, 'actual_hours', 0),
        "percent_complete": getattr(t, 'percent_complete', 0),
        "engineer": getattr(t, 'engineer', None),
        "is_critical": getattr(t, 'is_critical', False),
        "es": t.es, "ef": t.ef, "ls": t.ls, "lf": t.lf,
        "slack": t.slack,
    }
