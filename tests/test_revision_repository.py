"""Tests for RevisionRepository."""
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone, date
from models.enums import RevisionStatus


class TestRevisionRepository:
    """Tests for RevisionRepository."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return MagicMock()

    @pytest.fixture
    def repo(self, mock_db):
        """Create RevisionRepository with mocked database."""
        from repositories.revision_repository import RevisionRepository
        return RevisionRepository(db=mock_db)

    def test_get_by_id(self, repo, mock_db):
        """Test retrieving a revision by ID."""
        mock_db.fetch_one.return_value = {
            "id": 1, "document_id": 1, "revision_index": "1",
            "revision_letter": "A", "revision_number": 1,
            "version_number": 1, "status": "draft", "file_path": "/path/to/file.pdf",
            "change_log": "Initial revision", "created_by": 1,
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "approved_by": None, "approved_at": None
        }

        result = repo.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.revision_letter == "A"

    def test_get_by_id_not_found(self, repo, mock_db):
        """Test retrieving a non-existent revision."""
        mock_db.fetch_one.return_value = None

        result = repo.get_by_id(999)

        assert result is None

    def test_get_revisions_for_document(self, repo, mock_db):
        """Test retrieving revisions for a document."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "document_id": 1, "revision_index": "1",
                "revision_letter": "A", "revision_number": 1,
                "version_number": 1, "status": "draft", "file_path": "/path/file.pdf",
                "change_log": "Initial", "created_by": 1,
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "approved_by": None, "approved_at": None
            }
        ]

        result = repo.get_revisions_for_document(1)

        assert len(result) == 1
        assert result[0].document_id == 1

    def test_get_latest_version_number(self, repo, mock_db):
        """Test getting latest version number for a document."""
        mock_db.fetch_one.return_value = {"max_version": 5}

        result = repo.get_latest_version_number(1)

        assert result == 5

    def test_get_latest_version_number_no_revisions(self, repo, mock_db):
        """Test getting latest version when no revisions exist."""
        mock_db.fetch_one.return_value = {"max_version": 0}

        result = repo.get_latest_version_number(999)

        assert result == 0

    def test_get_latest_letter_and_number(self, repo, mock_db):
        """Test getting latest letter and number for a document."""
        mock_db.fetch_one.return_value = {"revision_letter": "B", "revision_number": 2}

        letter, number = repo.get_latest_letter_and_number(1)

        assert letter == "B"
        assert number == 2

    def test_get_latest_letter_and_number_no_revisions(self, repo, mock_db):
        """Test getting latest when no revisions exist."""
        mock_db.fetch_one.return_value = None

        letter, number = repo.get_latest_letter_and_number(999)

        assert letter == "A"
        assert number == 0

    def test_insert(self, repo, mock_db):
        """Test inserting a new revision."""
        mock_db.fetch_one.return_value = {
            "id": 2, "document_id": 1, "revision_index": "2",
            "revision_letter": "B", "revision_number": 2,
            "version_number": 2, "status": "draft", "file_path": "/path/file2.pdf",
            "change_log": "Updated", "created_by": 1,
            "created_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
            "approved_by": None, "approved_at": None
        }

        result = repo.insert(
            document_id=1, revision_index="2", revision_letter="B",
            revision_number=2, version_number=2, status=RevisionStatus.DRAFT,
            file_path="/path/file2.pdf", change_log="Updated", created_by=1
        )

        assert result is not None
        assert result.id == 2

    def test_get_latest_for_document(self, repo, mock_db):
        """Test getting latest revision for a document."""
        mock_db.fetch_one.return_value = {
            "id": 2, "document_id": 1, "revision_index": "2",
            "revision_letter": "B", "revision_number": 2,
            "version_number": 2, "status": "draft", "file_path": "/path/file2.pdf",
            "change_log": "Latest", "created_by": 1,
            "created_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
            "approved_by": None, "approved_at": None
        }

        result = repo.get_latest_for_document(1)

        assert result is not None
        assert result.version_number == 2

    def test_get_latest_for_document_not_found(self, repo, mock_db):
        """Test getting latest when no revisions exist."""
        mock_db.fetch_one.return_value = None

        result = repo.get_latest_for_document(999)

        assert result is None

    def test_mark_previous_revisions_superseded(self, repo, mock_db):
        """Test marking previous revisions as superseded."""
        repo.mark_previous_revisions_superseded(document_id=1, exclude_id=2)

        mock_db.execute.assert_called_once()

    def test_approve_revision(self, repo, mock_db):
        """Test approving a revision."""
        repo.approve_revision(revision_id=1, approved_by=2)

        mock_db.execute.assert_called_once()
