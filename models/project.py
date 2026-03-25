from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from models.enums import ProjectStatus


@dataclass
class Project:
    id: int
    code: str
    name: str
    customer: Optional[str]
    status: ProjectStatus
    manager_id: Optional[int]
    start_date: Optional[date]
    end_date_planned: Optional[date]
    end_date_forecast: Optional[date]
    end_date_actual: Optional[date]
    created_at: datetime
