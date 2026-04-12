"""Tests for DocumentService."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from models.document import Document
from models.enums import DocumentStatus


class TestDocumentService:
    """Tests for DocumentService business logic."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return MagicMock()

    @pytest.fixture
    def mock_document_repo(self, mock_db):
        """Create a mock document repository."""
        repo = MagicMock()
        return repo

    @pytest.fixture
    def service(self, mock_db, mock_document_repo):
        """Create DocumentService with mocked dependencies."""
        from services.document_service import DocumentService
        return DocumentService(db=mock_db, document_repo=mock_document_repo)

    def test_get_document(self, service, mock_document_repo):
        """Test retrieving a document by ID."""
        mock_doc = Document(
            id=1, project_id=1, code="DOC-001", title="Test Doc",
            discipline="Engineering", status=DocumentStatus.IN_WORK,
            current_revision_id=None, created_by=1,
            created_at=datetime(2026, 1, 1)
        )
        mock_document_repo.get_by_id.return_value = mock_doc

        result = service.get_document(1)

        assert result == mock_doc
        mock_document_repo.get_by_id.assert_called_once_with(1)

    def test_get_document_not_found(self, service, mock_document_repo):
        """Test retrieving a non-existent document."""
        mock_document_repo.get_by_id.return_value = None

        result = service.get_document(999)

        assert result is None

    def test_get_documents_for_project(self, service, mock_document_repo):
        """Test retrieving documents for a project."""
        mock_docs = [
            Document(
                id=1, project_id=1, code="DOC-001", title="Doc 1",
                discipline="Engineering", status=DocumentStatus.IN_WORK,
                current_revision_id=None, created_by=1,
                created_at=datetime(2026, 1, 1)
            ),
            Document(
                id=2, project_id=1, code="DOC-002", title="Doc 2",
                discipline="Piping", status=DocumentStatus.ON_REVIEW,
                current_revision_id=None, created_by=1,
                created_at=datetime(2026, 1, 2)
            ),
        ]
        mock_document_repo.get_by_project_id.return_value = mock_docs

        result = service.get_documents_for_project(1)

        assert len(result) == 2
        mock_document_repo.get_by_project_id.assert_called_once_with(1)

    def test_update_document_status(self, service, mock_document_repo, mock_db):
        """Test updating document status with transaction."""
        mock_db.transaction.return_value.__enter__ = MagicMock()
        mock_db.transaction.return_value.__exit__ = MagicMock()

        service.update_document_status(1, DocumentStatus.APPROVED)

        mock_db.transaction.assert_called_once()
        mock_document_repo.update_status.assert_called_once_with(1, DocumentStatus.APPROVED)

    def test_update_document_status_uses_transaction(self, service, mock_document_repo, mock_db):
        """Test that update_document_status uses database transaction."""
        mock_db.transaction.return_value.__enter__ = MagicMock()
        mock_db.transaction.return_value.__exit__ = MagicMock()

        service.update_document_status(1, DocumentStatus.ARCHIVED)

        # Verify transaction context manager was used
        assert mock_db.transaction.called
