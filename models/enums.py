from enum import StrEnum


class DocumentStatus(StrEnum):
    IN_WORK = "in_work"
    ON_REVIEW = "on_review"
    APPROVED = "approved"
    ARCHIVED = "archived"


class RevisionStatus(StrEnum):
    DRAFT = "draft"
    ON_REVIEW = "on_review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"


class TaskStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TaskType(StrEnum):
    ENGINEERING = "engineering"
    REVIEW = "review"
    APPROVAL = "approval"
    OTHER = "other"


class GamificationEventType(StrEnum):
    TASK_COMPLETED = "task_completed"
    CRITICAL_TASK_COMPLETED = "critical_task_completed"
    REVIEW_COMPLETED = "review_completed"
    APPROVAL_COMPLETED = "approval_completed"
    DOCUMENT_APPROVED = "document_approved"


class ProjectStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
