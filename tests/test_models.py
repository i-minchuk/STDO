from datetime import date, datetime

from models.enums import (
    DocumentStatus,
    ProjectStatus,
    RevisionStatus,
    TaskStatus,
    TaskType,
)
from models.document import Document
from models.project import Project
from models.revision import DocumentRevision
from models.planned_task import PlannedTask
from models.task_dependency import TaskDependency


def test_document_status_values():
    assert DocumentStatus.IN_WORK == "in_work"
    assert DocumentStatus.ON_REVIEW == "on_review"
    assert DocumentStatus.APPROVED == "approved"
    assert DocumentStatus.ARCHIVED == "archived"


def test_revision_status_values():
    assert RevisionStatus.DRAFT == "draft"
    assert RevisionStatus.APPROVED == "approved"
    assert RevisionStatus.SUPERSEDED == "superseded"


def test_project_status_values():
    assert ProjectStatus.PLANNED == "planned"
    assert ProjectStatus.ACTIVE == "active"
    assert ProjectStatus.COMPLETED == "completed"


def test_task_status_values():
    assert TaskStatus.NOT_STARTED == "not_started"
    assert TaskStatus.IN_PROGRESS == "in_progress"
    assert TaskStatus.COMPLETED == "completed"
    assert TaskStatus.BLOCKED == "blocked"


def test_task_type_values():
    assert TaskType.ENGINEERING == "engineering"
    assert TaskType.REVIEW == "review"
    assert TaskType.APPROVAL == "approval"


def test_document_model():
    doc = Document(
        id=1,
        project_id=1,
        code="DOC-001",
        title="Test Doc",
        discipline="Piping",
        status=DocumentStatus.IN_WORK,
        current_revision_id=None,
        created_by=1,
        created_at=datetime(2026, 1, 1),
    )
    assert doc.code == "DOC-001"
    assert doc.status == DocumentStatus.IN_WORK


def test_project_model():
    project = Project(
        id=1,
        code="PRJ-001",
        name="Test Project",
        customer="Test Customer",
        status=ProjectStatus.ACTIVE,
        manager_id=2,
        start_date=date(2026, 1, 1),
        end_date_planned=date(2026, 12, 31),
        end_date_forecast=None,
        end_date_actual=None,
        created_at=datetime(2026, 1, 1),
    )
    assert project.code == "PRJ-001"
    assert project.status == ProjectStatus.ACTIVE


def test_revision_model():
    rev = DocumentRevision(
        id=1,
        document_id=1,
        revision_index="A01",
        revision_letter="A",
        revision_number=1,
        version_number=1,
        status=RevisionStatus.DRAFT,
        file_path="/tmp/test.pdf",
        change_log="Initial",
        created_by=1,
        created_at=datetime(2026, 1, 1),
        approved_by=None,
        approved_at=None,
    )
    assert rev.revision_index == "A01"
    assert rev.status == RevisionStatus.DRAFT


def test_planned_task_model():
    task = PlannedTask(
        id=1,
        project_id=1,
        project_code="PRJ-001",
        project_name="Test",
        document_id=None,
        document_code=None,
        revision_id=None,
        revision_index=None,
        name="Engineering Task",
        task_type=TaskType.ENGINEERING,
        assigned_to=1,
        owner_name="Test User",
        duration_days_planned=5,
        work_hours_planned=40.0,
        start_date_planned=date(2026, 3, 1),
        end_date_planned=date(2026, 3, 5),
        start_date_actual=None,
        end_date_actual=None,
        percent_complete=0,
        status=TaskStatus.NOT_STARTED,
    )
    assert task.name == "Engineering Task"
    assert task.slack is None


def test_task_dependency_model():
    dep = TaskDependency(
        id=1,
        project_id=1,
        predecessor_task_id=1,
        successor_task_id=2,
        dependency_type="FS",
        lag_days=0,
    )
    assert dep.dependency_type == "FS"
    assert dep.lag_days == 0
