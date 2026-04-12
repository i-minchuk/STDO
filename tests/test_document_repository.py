"""Tests for DocumentRepository."""
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
from models.enums import DocumentStatus


class TestDocumentRepository:
    """Tests for DocumentRepository."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return MagicMock()

    @pytest.fixture
    def repo(self, mock_db):
        """Create DocumentRepository with mocked database."""
        from repositories.document_repository import DocumentRepository
        return DocumentRepository(db=mock_db)

    def test_get_by_id(self, repo, mock_db):
        """Test retrieving a document by ID."""
        mock_db.fetch_one.return_value = {
            "id": 1, "project_id": 1, "code": "DOC-001", "title": "Test Document",
            "discipline": "Engineering", "status": "in_work",
            "current_revision_id": None, "created_by": 1,
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc)
        }

        result = repo.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.code == "DOC-001"

    def test_get_by_id_not_found(self, repo, mock_db):
        """Test retrieving a non-existent document."""
        mock_db.fetch_one.return_value = None

        result = repo.get_by_id(999)

        assert result is None

    def test_get_by_project_id(self, repo, mock_db):
        """Test retrieving documents for a project."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "project_id": 1, "code": "DOC-001", "title": "Doc 1",
                "discipline": "Engineering", "status": "in_work",
                "current_revision_id": None, "created_by": 1,
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc)
            },
            {
                "id": 2, "project_id": 1, "code": "DOC-002", "title": "Doc 2",
                "discipline": "Piping", "status": "on_review",
                "current_revision_id": None, "created_by": 1,
                "created_at": datetime(2026, 1, 2, tzinfo=timezone.utc)
            }
        ]

        result = repo.get_by_project_id(1)

        assert len(result) == 2
        assert result[0].project_id == 1

    def test_get_all(self, repo, mock_db):
        """Test retrieving all documents."""
        mock_db.fetch_all.return_value = []

        result = repo.get_all()

        assert result == []

    def test_search_paginated_no_filters(self, repo, mock_db):
        """Test searching documents with no filters."""
        mock_db.fetch_all.return_value = []
        mock_db.fetch_one.return_value = {"cnt": 0}

        result, total = repo.search_paginated(limit=10, offset=0)

        assert result == []
        assert total == 0

    def test_search_paginated_with_project_filter(self, repo, mock_db):
        """Test searching documents filtered by project."""
        mock_db.fetch_all.return_value = []
        mock_db.fetch_one.return_value = {"cnt": 0}

        result, total = repo.search_paginated(project_id=1, limit=10, offset=0)

        assert result == []
        assert total == 0

    def test_search_paginated_with_status_filter(self, repo, mock_db):
        """Test searching documents filtered by status."""
        mock_db.fetch_all.return_value = []
        mock_db.fetch_one.return_value = {"cnt": 0}

        result, total = repo.search_paginated(
            status=DocumentStatus.IN_WORK, limit=10, offset=0
        )

        assert result == []
        assert total == 0

    def test_search_paginated_with_search_term(self, repo, mock_db):
        """Test searching documents with search term."""
        mock_db.fetch_all.return_value = []
        mock_db.fetch_one.return_value = {"cnt": 0}

        result, total = repo.search_paginated(search="test", limit=10, offset=0)

        assert result == []
        assert total == 0

    def test_insert(self, repo, mock_db):
        """Test inserting a new document."""
        mock_db.fetch_one.return_value = {
            "id": 2, "project_id": 1, "code": "DOC-002", "title": "New Document",
            "discipline": "Electrical", "status": "in_work",
            "current_revision_id": None, "created_by": 1,
            "created_at": datetime(2026, 1, 2, tzinfo=timezone.utc)
        }

        result = repo.insert(
            project_id=1, code="DOC-002", title="New Document",
            discipline="Electrical", status=DocumentStatus.IN_WORK, created_by=1
        )

        assert result is not None
        assert result.id == 2

    def test_update_status(self, repo, mock_db):
        """Test updating document status."""
        repo.update_status(1, DocumentStatus.APPROVED)

        mock_db.execute.assert_called_once()

    def test_update_status_with_revision(self, repo, mock_db):
        """Test updating document status with current revision."""
        repo.update_status(1, DocumentStatus.APPROVED, current_revision_id=5)

        mock_db.execute.assert_called_once()

    def test_update_current_revision(self, repo, mock_db):
        """Test updating document's current revision."""
        repo.update_current_revision(document_id=1, revision_id=5)

        mock_db.execute.assert_called_once()

    def test_count_by_project_and_status(self, repo, mock_db):
        """Test counting documents by project and status."""
        mock_db.fetch_one.return_value = {"cnt": 5}

        result = repo.count_by_project_and_status(1, DocumentStatus.IN_WORK)

        assert result == 5
