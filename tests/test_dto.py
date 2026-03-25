"""Tests for DTO validation (Pydantic models)."""

from datetime import date, datetime

from dto.common import DocumentShortDTO, ProjectShortDTO
from dto.revision import (
    ApproveRevisionRequestDTO,
    CreateRevisionRequestDTO,
    RevisionDTO,
    RevisionWorkflowDTO,
    WorkflowTaskDTO,
)
from dto.portfolio_today import (
    PortfolioSummaryDTO,
    ProjectHealthDTO,
    ProjectTodayOverviewDTO,
    ProjectTodayWorkloadDTO,
)


def test_project_short_dto():
    dto = ProjectShortDTO(id=1, code="PRJ-001", name="Test", status="active")
    assert dto.id == 1
    assert dto.status == "active"


def test_document_short_dto():
    dto = DocumentShortDTO(
        id=1,
        project_id=1,
        project_code="PRJ-001",
        code="DOC-001",
        title="Test",
        status="in_work",
        current_revision_id=None,
    )
    assert dto.code == "DOC-001"


def test_create_revision_request_dto_defaults():
    dto = CreateRevisionRequestDTO(created_by=1)
    assert dto.major is False
    assert dto.review_duration_days == 2
    assert dto.approval_duration_days == 1
    assert dto.reviewer_id is None
    assert dto.approver_id is None


def test_approve_revision_request_dto():
    dto = ApproveRevisionRequestDTO(approved_by=1, comment="Looks good")
    assert dto.approved_by == 1
    assert dto.comment == "Looks good"


def test_approve_revision_request_dto_no_comment():
    dto = ApproveRevisionRequestDTO(approved_by=1)
    assert dto.comment is None


def test_revision_dto():
    dto = RevisionDTO(
        id=1,
        document_id=1,
        revision_index="A01",
        revision_letter="A",
        revision_number=1,
        version_number=1,
        status="draft",
        file_name="test.pdf",
        file_path="/tmp/test.pdf",
        change_log="Initial",
        created_by=1,
        created_at=datetime(2026, 1, 1),
        approved_by=None,
        approved_at=None,
    )
    assert dto.revision_index == "A01"


def test_workflow_task_dto():
    dto = WorkflowTaskDTO(
        task_id=1,
        name="Review DOC-001",
        task_type="review",
        assigned_to=2,
        status="not_started",
        start_date_planned=date(2026, 3, 1),
        end_date_planned=date(2026, 3, 3),
    )
    assert dto.task_type == "review"


def test_revision_workflow_dto_empty():
    dto = RevisionWorkflowDTO(review_task=None, approval_task=None)
    assert dto.review_task is None


def test_project_health_dto():
    dto = ProjectHealthDTO(
        percent_complete=75.0,
        spi=0.95,
        cpi=1.02,
        schedule_risk_level="low",
        cost_risk_level="low",
    )
    assert dto.percent_complete == 75.0


def test_portfolio_summary_dto():
    dto = PortfolioSummaryDTO(
        projects_total=5,
        projects_at_risk=1,
        avg_spi=0.9,
        avg_cpi=1.0,
        total_capacity_hours_today=80.0,
        total_planned_hours_today=64.0,
        total_logged_hours_today=40.0,
    )
    assert dto.projects_total == 5
