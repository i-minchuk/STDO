from dataclasses import dataclass
from datetime import datetime
from .enums import GamificationEventType


@dataclass
class EngineerMetric:
    id: int
    user_id: int
    total_points: int
    xp: int
    rank: str
    tasks_completed: int
    documents_closed: int
    last_updated_at: datetime