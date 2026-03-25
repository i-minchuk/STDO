from dataclasses import dataclass


@dataclass
class TaskDependency:
    id: int
    project_id: int
    predecessor_task_id: int
    successor_task_id: int
    dependency_type: str  # 'FS'
    lag_days: int