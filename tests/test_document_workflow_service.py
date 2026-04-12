"""Tests for DocumentWorkflowService."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from io import BytesIO


class TestDocumentWorkflowService:
    """Tests for DocumentWorkflowService business logic."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return MagicMock()

    @pytest.fixture
    def mock_revision_service(self):
        """Create a mock revision service."""
        return MagicMock()

    @pytest.fixture
    def mock_document_repo(self):
        """Create a mock document repository."""
        return MagicMock()

    @pytest.fixture
    def mock_revision_repo(self):
        """Create a mock revision repository."""
        return MagicMock()

    @pytest.fixture
    def mock_project_repo(self):
        """Create a mock project repository."""
        return MagicMock()

    @pytest.fixture
    def mock_task_repo(self):
        """Create a mock task repository."""
        return MagicMock()

    @pytest.fixture
    def mock_dep_repo(self):
        """Create a mock dependency repository."""
        return MagicMock()

    @pytest.fixture
    def mock_cpm(self):
        """Create a mock CPM scheduler."""
        return MagicMock()

    @pytest.fixture
    def mock_dashboard(self):
        """Create a mock project dashboard."""
        return MagicMock()

    @pytest.fixture
    def service(
        self, mock_db, mock_revision_service, mock_document_repo, mock_revision_repo,
        mock_project_repo, mock_task_repo, mock_dep_repo, mock_cpm, mock_dashboard
    ):
        """Create DocumentWorkflowService with mocked dependencies."""
        from services.document_workflow_service import DocumentWorkflowService
        return DocumentWorkflowService(
            db=mock_db,
            revision_service=mock_revision_service,
            document_repo=mock_document_repo,
            revision_repo=mock_revision_repo,
            project_repo=mock_project_repo,
            task_repo=mock_task_repo,
            dep_repo=mock_dep_repo,
            cpm_scheduler=mock_cpm,
            project_dashboard=mock_dashboard,
        )

    def test_create_revision_with_workflow(
        self, service, mock_revision_service, mock_document_repo, mock_project_repo,
        mock_task_repo, mock_dep_repo
    ):
        """Test creating a revision with workflow tasks."""
        from models.revision import DocumentRevision
        from models.enums import RevisionStatus

        mock_revision = DocumentRevision(
            id=1, document_id=1, revision_index="A1", revision_letter="A",
            revision_number=1, version_number=1, status=RevisionStatus.DRAFT,
            file_path="/path/file.pdf", change_log="Initial", created_by=1,
            created_at=None, approved_by=None, approved_at=None
        )
        mock_revision_service.create_revision.return_value = mock_revision

        mock_document = MagicMock(id=1, code="DOC-001", project_id=1)
        mock_document_repo.get_by_id.return_value = mock_document

        mock_project = MagicMock(id=1, code="PRJ-001", name="Test Project")
        mock_project_repo.get_by_id.return_value = mock_project

        mock_review_task = MagicMock(
            id=1, end_date_planned=date(2026, 1, 3)
        )
        mock_task_repo.insert.side_effect = [mock_review_task, MagicMock(id=2)]

        file_content = BytesIO(b"test content")

        result = service.create_revision_with_workflow(
            document_id=1,
            filename="test.pdf",
            file_content=file_content,
            change_log="Initial",
            created_by=1,
            reviewer_id=2,
            approver_id=3,
            review_duration_days=2,
            approval_duration_days=1,
        )

        assert result == mock_revision
        mock_revision_service.create_revision.assert_called_once()
        assert mock_task_repo.insert.call_count == 2

    def test_approve_revision_with_workflow(
        self, service, mock_revision_service, mock_revision_repo,
        mock_document_repo, mock_task_repo
    ):
        """Test approving a revision with workflow completion."""
        from models.revision import DocumentRevision
        from models.enums import RevisionStatus, TaskStatus
        from models.enums import TaskType

        mock_revision = DocumentRevision(
            id=1, document_id=1, revision_index="A1", revision_letter="A",
            revision_number=1, version_number=1, status=RevisionStatus.ON_REVIEW,
            file_path="/path/file.pdf", change_log="Updated", created_by=1,
            created_at=None, approved_by=None, approved_at=None
        )
        mock_revision_repo.get_by_id.return_value = mock_revision

        mock_document = MagicMock(id=1, code="DOC-001", project_id=1)
        mock_document_repo.get_by_id.return_value = mock_document

        mock_approval_task = MagicMock(
            id=2, task_type=TaskType.APPROVAL, status=TaskStatus.NOT_STARTED,
            start_date_actual=date(2026, 1, 1), actual_hours=8.0
        )
        mock_task_repo.get_by_revision_id.return_value = [mock_approval_task]

        result = service.approve_revision_with_workflow_dto(1, 2, "Approved")

        assert result["revision_id"] == 1
        assert result["status"] == "approved"
        assert result["approved_by"] == 2
        mock_revision_service.approve_revision.assert_called_once()
        mock_task_repo.update_progress.assert_called_once()

    def test_get_workflow_tasks_for_revision(
        self, service, mock_task_repo
    ):
        """Test getting workflow tasks for a revision."""
        from models.planned_task import PlannedTask
        from models.enums import TaskType, TaskStatus

        review_task = PlannedTask(
            id=1, project_id=1, project_code="PRJ-001", project_name="Test",
            document_id=1, document_code="DOC-001", revision_id=1, revision_index="A1",
            name="Review DOC-001 A1", task_type=TaskType.REVIEW, assigned_to=2,
            owner_name="Reviewer", duration_days_planned=2, work_hours_planned=16.0,
            start_date_planned=date(2026, 1, 1), end_date_planned=date(2026, 1, 3),
            start_date_actual=None, end_date_actual=None,
            percent_complete=0, status=TaskStatus.NOT_STARTED,
            es=None, ef=None, ls=None, lf=None, slack=None, actual_hours=None
        )
        mock_task_repo.get_by_revision_id.return_value = [review_task]

        result = service.get_workflow_tasks_for_revision(1)

        assert result.review_task is not None
        assert result.review_task.task_type == "review"
        assert result.approval_task is None

    def test_create_revision_document_not_found(
        self, service, mock_revision_service, mock_document_repo
    ):
        """Test creating revision when document not found."""
        mock_revision_service.create_revision.return_value = MagicMock()
        mock_document_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Document 1 not found"):
            service.create_revision_with_workflow(
                document_id=1, filename="test.pdf",
                file_content=BytesIO(b"test"), change_log="Test", created_by=1
            )

    def test_create_revision_project_not_found(
        self, service, mock_revision_service, mock_document_repo, mock_project_repo
    ):
        """Test creating revision when project not found."""
        mock_revision_service.create_revision.return_value = MagicMock()
        mock_document = MagicMock(id=1, code="DOC-001", project_id=1)
        mock_document_repo.get_by_id.return_value = mock_document
        mock_project_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Project 1 not found"):
            service.create_revision_with_workflow(
                document_id=1, filename="test.pdf",
                file_content=BytesIO(b"test"), change_log="Test", created_by=1
            )
