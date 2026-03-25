from dataclasses import dataclass
from datetime import date
from typing import Optional
from .enums import TaskStatus, TaskType


@dataclass
class PlannedTask:
    id: int
    project_id: int
    project_code: str
    project_name: str
    document_id: Optional[int]
    document_code: Optional[str]
    revision_id: Optional[int]
    revision_index: Optional[str]
    name: str
    task_type: TaskType
    assigned_to: Optional[int]
    owner_name: Optional[str]
    duration_days_planned: int
    work_hours_planned: float
    start_date_planned: Optional[date]
    end_date_planned: Optional[date]
    start_date_actual: Optional[date]
    end_date_actual: Optional[date]
    percent_complete: int
    status: TaskStatus

    es: Optional[int] = None
    ef: Optional[int] = None
    ls: Optional[int] = None
    lf: Optional[int] = None
    slack: Optional[int] = None

    actual_hours: Optional[float] = None