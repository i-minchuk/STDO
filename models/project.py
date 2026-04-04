from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, Any

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
    # Гибкие поля для кастомных атрибутов проекта (требования заказчика)
    custom_fields: Optional[Dict[str, Any]] = None
    # Специфические поля для тендеров
    vdr_required: bool = False
    otk_required: bool = False
    crs_deadline_days: int = 3
    logistics_delivery_weeks: int = 2
    logistics_complexity: str = "normal"
