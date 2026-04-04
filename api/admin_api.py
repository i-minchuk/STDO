from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from core.auth import get_current_user
from core.service_locator import get_locator
from models.user import User

router = APIRouter(prefix="/api/admin/work-schedules", tags=["admin"])


class WorkScheduleCreateRequest(BaseModel):
    name: str
    work_days: List[int]
    start_time_hours: float
    end_time_hours: float
    lunch_duration_hours: float
    is_default: bool = False


class WorkScheduleUpdateRequest(BaseModel):
    name: Optional[str] = None
    work_days: Optional[List[int]] = None
    start_time_hours: Optional[float] = None
    end_time_hours: Optional[float] = None
    lunch_duration_hours: Optional[float] = None
    is_default: Optional[bool] = None


def _is_admin(user: User) -> bool:
    """Check if user is admin."""
    return user.role in ("admin", "manager")


@router.get("/")
def list_schedules(current_user: User = Depends(get_current_user)):
    """List all work schedules."""
    if not _is_admin(current_user):
        raise HTTPException(403, "Only admins can view work schedules")
    
    loc = get_locator()
    schedules = loc.work_schedule_repo.get_all_schedules()
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "work_days": s.work_days,
            "start_time_hours": float(s.start_time_hours),
            "end_time_hours": float(s.end_time_hours),
            "lunch_duration_hours": float(s.lunch_duration_hours),
            "work_hours_per_day": round(s.work_hours_per_day, 2),
            "work_hours_per_week": round(s.work_hours_per_week, 2),
            "is_default": s.is_default,
        }
        for s in schedules
    ]


@router.get("/default")
def get_default_schedule(current_user: User = Depends(get_current_user)):
    """Get default work schedule (public endpoint)."""
    loc = get_locator()
    schedule = loc.work_schedule_repo.get_default_schedule()
    
    if not schedule:
        raise HTTPException(500, "No default work schedule configured")
    
    return {
        "id": schedule.id,
        "name": schedule.name,
        "work_days": schedule.work_days,
        "start_time_hours": float(schedule.start_time_hours),
        "end_time_hours": float(schedule.end_time_hours),
        "lunch_duration_hours": float(schedule.lunch_duration_hours),
        "work_hours_per_day": round(schedule.work_hours_per_day, 2),
        "work_hours_per_week": round(schedule.work_hours_per_week, 2),
    }


@router.post("/")
def create_schedule(
    body: WorkScheduleCreateRequest,
    current_user: User = Depends(get_current_user),
):
    """Create new work schedule."""
    if not _is_admin(current_user):
        raise HTTPException(403, "Only admins can create work schedules")
    
    loc = get_locator()
    schedule = loc.work_schedule_repo.create_schedule(
        name=body.name,
        work_days=body.work_days,
        start_time_hours=body.start_time_hours,
        end_time_hours=body.end_time_hours,
        lunch_duration_hours=body.lunch_duration_hours,
        is_default=body.is_default,
    )
    
    return {
        "id": schedule.id,
        "name": schedule.name,
        "work_days": schedule.work_days,
        "start_time_hours": float(schedule.start_time_hours),
        "end_time_hours": float(schedule.end_time_hours),
        "lunch_duration_hours": float(schedule.lunch_duration_hours),
        "work_hours_per_day": round(schedule.work_hours_per_day, 2),
        "work_hours_per_week": round(schedule.work_hours_per_week, 2),
        "is_default": schedule.is_default,
    }


@router.put("/{schedule_id}")
def update_schedule(
    schedule_id: int,
    body: WorkScheduleUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """Update work schedule."""
    if not _is_admin(current_user):
        raise HTTPException(403, "Only admins can update work schedules")
    
    loc = get_locator()
    schedule = loc.work_schedule_repo.update_schedule(
        schedule_id=schedule_id,
        name=body.name,
        work_days=body.work_days,
        start_time_hours=body.start_time_hours,
        end_time_hours=body.end_time_hours,
        lunch_duration_hours=body.lunch_duration_hours,
        is_default=body.is_default,
    )
    
    if not schedule:
        raise HTTPException(404, "Schedule not found")
    
    return {
        "id": schedule.id,
        "name": schedule.name,
        "work_days": schedule.work_days,
        "start_time_hours": float(schedule.start_time_hours),
        "end_time_hours": float(schedule.end_time_hours),
        "lunch_duration_hours": float(schedule.lunch_duration_hours),
        "work_hours_per_day": round(schedule.work_hours_per_day, 2),
        "work_hours_per_week": round(schedule.work_hours_per_week, 2),
        "is_default": schedule.is_default,
    }


@router.post("/calculate/hours-to-days")
def calculate_hours_to_days(
    work_hours: float,
    current_user: User = Depends(get_current_user),
):
    """Convert work hours to work days."""
    loc = get_locator()
    work_days = loc.time_calculation.calculate_work_days_from_hours(work_hours)
    
    schedule = loc.work_schedule_repo.get_default_schedule()
    return {
        "work_hours": work_hours,
        "work_days": work_days,
        "work_hours_per_day": round(schedule.work_hours_per_day, 2) if schedule else 8.0,
    }


@router.post("/calculate/days-to-hours")
def calculate_days_to_hours(
    work_days: int,
    current_user: User = Depends(get_current_user),
):
    """Convert work days to work hours."""
    loc = get_locator()
    work_hours = loc.time_calculation.calculate_hours_from_work_days(work_days)
    
    schedule = loc.work_schedule_repo.get_default_schedule()
    return {
        "work_days": work_days,
        "work_hours": round(work_hours, 2),
        "work_hours_per_day": round(schedule.work_hours_per_day, 2) if schedule else 8.0,
    }


@router.post("/calculate/end-date")
def calculate_end_date(
    start_date: date,
    work_days: int,
    current_user: User = Depends(get_current_user),
):
    """Calculate end date given start date and work days."""
    loc = get_locator()
    end_date = loc.time_calculation.calculate_end_date(start_date, work_days)
    work_count = loc.time_calculation.count_work_days_between(start_date, end_date)
    
    return {
        "start_date": str(start_date),
        "work_days_duration": work_days,
        "end_date": str(end_date),
        "actual_work_days": work_count,
    }
