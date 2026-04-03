from __future__ import annotations
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from typing import Optional
from core.auth import get_current_user
from core.service_locator import get_locator
from models.user import User
from models.enums import TaskStatus

router = APIRouter(prefix="/api/workload", tags=["workload"])

WORK_HOURS_PER_DAY = 8


@router.get("/engineers")
def engineer_workload(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Анализ загруженности всех инженеров: текущая нагрузка, свободный ресурс, % загрузки."""
    loc = get_locator()
    tasks = loc.planned_task_repo.get_all()

    today = date.today()
    d_from = date.fromisoformat(date_from) if date_from else today
    d_to = date.fromisoformat(date_to) if date_to else today + timedelta(days=30)
    work_days = max(1, sum(1 for d in range((d_to - d_from).days + 1)
                           if (d_from + timedelta(days=d)).weekday() < 5))
    total_capacity_hours = work_days * WORK_HOURS_PER_DAY

    by_eng = {}
    for t in tasks:
        eng = t.owner_name or "Не назначен"
        if eng not in by_eng:
            by_eng[eng] = {
                "total_tasks": 0, "active_tasks": 0, "completed_tasks": 0,
                "planned_hours": 0, "actual_hours": 0, "remaining_hours": 0,
                "overdue_tasks": 0,
            }
        data = by_eng[eng]
        data["total_tasks"] += 1
        ph = t.work_hours_planned or 0
        ah = t.actual_hours or 0

        if t.status == TaskStatus.COMPLETED:
            data["completed_tasks"] += 1
        else:
            data["active_tasks"] += 1
            data["planned_hours"] += ph
            data["remaining_hours"] += max(0, ph - ah)
            if t.end_date_planned and t.end_date_planned < today:
                data["overdue_tasks"] += 1
        data["actual_hours"] += ah

    result = []
    for eng, data in sorted(by_eng.items()):
        utilization = round(data["remaining_hours"] / total_capacity_hours * 100, 1) if total_capacity_hours > 0 else 0
        free_hours = max(0, total_capacity_hours - data["remaining_hours"])
        result.append({
            "engineer": eng,
            "total_tasks": data["total_tasks"],
            "active_tasks": data["active_tasks"],
            "completed_tasks": data["completed_tasks"],
            "planned_hours": round(data["planned_hours"], 1),
            "actual_hours": round(data["actual_hours"], 1),
            "remaining_hours": round(data["remaining_hours"], 1),
            "capacity_hours": round(total_capacity_hours, 1),
            "free_hours": round(free_hours, 1),
            "utilization_pct": min(utilization, 100),
            "overdue_tasks": data["overdue_tasks"],
            "status": "overloaded" if utilization > 100 else ("busy" if utilization > 80 else "available"),
        })
    return {
        "period": {"from": str(d_from), "to": str(d_to), "work_days": work_days},
        "engineers": result,
        "summary": {
            "total_engineers": len(result),
            "overloaded": sum(1 for e in result if e["status"] == "overloaded"),
            "busy": sum(1 for e in result if e["status"] == "busy"),
            "available": sum(1 for e in result if e["status"] == "available"),
        },
    }
