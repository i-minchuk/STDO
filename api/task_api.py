from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.auth import get_current_user
from core.service_locator import get_locator
from models.user import User
from models.enums import TaskStatus

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class StatusUpdate(BaseModel):
    status: str

class TimeLog(BaseModel):
    minutes: int


@router.get("/today")
def today_tasks(current_user: User = Depends(get_current_user)):
    loc = get_locator()
    today = date.today()
    tasks = loc.planned_task_repo.get_all()
    result = []
    for t in tasks:
        if t.status == TaskStatus.COMPLETED:
            continue
        if t.start_date_planned and t.start_date_planned <= today:
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
    try:
        new_status = TaskStatus(body.status)
    except ValueError:
        raise HTTPException(400, f"Invalid status: {body.status}")

    loc.planned_task_repo.update_progress(
        task_id=task_id,
        percent_complete=100 if new_status == TaskStatus.COMPLETED else task.percent_complete,
        start_date_actual=task.start_date_actual,
        end_date_actual=date.today() if new_status == TaskStatus.COMPLETED else task.end_date_actual,
        actual_hours=task.actual_hours,
        status=new_status,
    )
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
        "id": t.id,
        "project_id": t.project_id,
        "document_id": t.document_id,
        "task_type": t.task_type.value if t.task_type else None,
        "name": t.name,
        "status": t.status.value,
        "start_date_planned": str(t.start_date_planned) if t.start_date_planned else None,
        "end_date_planned": str(t.end_date_planned) if t.end_date_planned else None,
        "work_hours_planned": t.work_hours_planned,
        "actual_hours": t.actual_hours,
        "percent_complete": t.percent_complete,
        "assigned_to": t.assigned_to,
        "es": t.es,
        "ef": t.ef,
        "ls": t.ls,
        "lf": t.lf,
        "slack": t.slack,
    }
