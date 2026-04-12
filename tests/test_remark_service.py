"""Tests for RemarkService."""
import pytest
from unittest.mock import MagicMock
from models.remark import Remark, RemarkResponse
from models.enums import RemarkStatus


class TestRemarkService:
    """Tests for RemarkService business logic."""

    @pytest.fixture
    def mock_remark_repo(self):
        """Create a mock remark repository."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_remark_repo):
        """Create RemarkService with mocked dependencies."""
        from services.remark_service import RemarkService
        return RemarkService(remark_repo=mock_remark_repo)

    def test_get_project_remarks(self, service, mock_remark_repo):
        """Test retrieving remarks for a project."""
        mock_remarks = [
            Remark(
                id=1, project_id=1, document_id=None, revision_id=None,
                author_id=1, author_name="Author", assignee_id=2,
                assignee_name="Assignee", source="internal",
                text="Test remark", status="open", resolution_comment=None,
                created_at=None, resolved_at=None, responses=[]
            ),
        ]
        mock_remark_repo.get_by_project.return_value = mock_remarks

        result = service.get_project_remarks(1)

        assert len(result) == 1
        mock_remark_repo.get_by_project.assert_called_once_with(1, None)

    def test_get_project_remarks_with_status_filter(self, service, mock_remark_repo):
        """Test retrieving remarks with status filter."""
        mock_remark_repo.get_by_project.return_value = []

        service.get_project_remarks(1, status="open")

        mock_remark_repo.get_by_project.assert_called_once_with(1, "open")

    def test_create_remark(self, service, mock_remark_repo):
        """Test creating a new remark."""
        mock_remark = Remark(
            id=1, project_id=1, document_id=None, revision_id=None,
            author_id=1, author_name="Author", assignee_id=None,
            assignee_name=None, source="internal",
            text="New remark", status="open", resolution_comment=None,
            created_at=None, resolved_at=None, responses=[]
        )
        mock_remark_repo.create.return_value = mock_remark

        result = service.create_remark(
            project_id=1, text="New remark", author_id=1,
            document_id=None, assignee_id=None, source="internal"
        )

        assert result == mock_remark
        mock_remark_repo.create.assert_called_once()

    def test_create_remark_strips_text(self, service, mock_remark_repo):
        """Test that remark text is stripped."""
        mock_remark_repo.create.return_value = MagicMock()

        service.create_remark(project_id=1, text="  text with spaces  ", author_id=1)

        # Verify text was stripped
        call_args = mock_remark_repo.create.call_args
        assert call_args[0][1] == "text with spaces"

    def test_create_remark_empty_text_raises(self, service):
        """Test that empty remark text raises ValueError."""
        with pytest.raises(ValueError, match="Текст замечания не может быть пустым"):
            service.create_remark(project_id=1, text="   ", author_id=1)

    def test_resolve_remark(self, service, mock_remark_repo):
        """Test resolving a remark."""
        mock_remark = MagicMock()
        mock_remark_repo.update_status.return_value = mock_remark

        result = service.resolve_remark(1, "resolved", "Fixed")

        assert result == mock_remark
        mock_remark_repo.update_status.assert_called_once_with(1, "resolved", "Fixed")

    def test_resolve_remark_invalid_status_raises(self, service):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError, match="Недопустимый статус"):
            service.resolve_remark(1, "invalid_status")

    def test_resolve_remark_open_status_raises(self, service):
        """Test that resolving to 'open' status raises ValueError."""
        with pytest.raises(ValueError, match="Нельзя вернуть статус 'open'"):
            service.resolve_remark(1, "open")

    def test_resolve_remark_not_found_raises(self, service, mock_remark_repo):
        """Test that non-existent remark raises ValueError."""
        mock_remark_repo.update_status.return_value = None

        with pytest.raises(ValueError, match="Замечание #1 не найдено"):
            service.resolve_remark(1, "resolved")

    def test_add_response(self, service, mock_remark_repo):
        """Test adding a response to a remark."""
        mock_response = RemarkResponse(
            id=1, remark_id=1, author_id=2, author_name="Responder",
            text="Response text", created_at=None
        )
        mock_remark_repo.add_response.return_value = mock_response

        result = service.add_response(1, 2, "Response text")

        assert result == mock_response
        mock_remark_repo.add_response.assert_called_once_with(1, 2, "Response text")

    def test_add_response_empty_text_raises(self, service):
        """Test that empty response text raises ValueError."""
        with pytest.raises(ValueError, match="Текст ответа не может быть пустым"):
            service.add_response(1, 2, "   ")
