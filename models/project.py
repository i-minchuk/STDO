from datetime import date, datetime
from typing import Optional
from models.enums import ProjectStatus  # сделай enum наподобие TaskStatus


class Project:
    id: int
    code: str                 # Короткий код проекта, вроде "P-001"
    name: str                 # Название проекта
    client_name: Optional[str]
    status: ProjectStatus
    start_date_planned: Optional[date]
    end_date_planned: Optional[date]
    start_date_actual: Optional[date]
    end_date_actual: Optional[date]
    created_by: int
    created_at: datetime