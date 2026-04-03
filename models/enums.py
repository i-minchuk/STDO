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

class RemarkStatus(StrEnum):
    OPEN       = "open"
    RESOLVED   = "resolved"    # Проблема решена
    REJECTED   = "rejected"    # Ошибочно назначено
    SUPERSEDED = "superseded"  # Снято в связи с изменением ТЗ

class RemarkSource(StrEnum):
    INTERNAL = "internal"
    CUSTOMER = "customer"
    REVIEWER = "reviewer"

class ValidationProfile(StrEnum):
    ESKD             = "ESKD"
    GOST_R           = "GOST_R"
    CUSTOMER_GAZPROM = "CUSTOMER_GAZPROM"
    CUSTOMER_ROSATOM = "CUSTOMER_ROSATOM"

class GamificationAction(StrEnum):
    DOC_UPLOADED      = "doc_uploaded"
    DOC_PASSED_GOST   = "doc_passed_gost"
    REMARK_CLOSED     = "remark_closed"
    SUBMITTED_ON_TIME = "submitted_on_time"
    SUBMITTED_EARLY   = "submitted_early"
    REVISION_CLEAN    = "revision_clean"
    STREAK_5          = "streak_5"
    OVERDUE           = "overdue"