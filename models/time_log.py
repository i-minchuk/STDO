from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class TimeLog:
    id: int
    user_id: int
    project_id: int
    document_id: Optional[int]
    task_id: Optional[int]
    day: date
    hours: float
    description: Optional[str]