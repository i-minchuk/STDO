"""Tests for RemarkRepository."""
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone


class TestRemarkRepository:
    """Tests for RemarkRepository."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return MagicMock()

    @pytest.fixture
    def repo(self, mock_db):
        """Create RemarkRepository with mocked database."""
        from repositories.remark_repository import RemarkRepository
        return RemarkRepository(db=mock_db)

    def test_get_by_project(self, repo, mock_db):
        """Test getting remarks for a project."""
        mock_db.fetch_all.side_effect = [
            [  # Main query
                {
                    "id": 1, "project_id": 1, "document_id": None, "revision_id": None,
                    "author_id": 1, "author_name": "Author", "assignee_id": 2, "assignee_name": "Assignee",
                    "source": "internal", "text": "Test remark", "status": "open", "resolution_comment": None,
                    "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc), "resolved_at": None
                }
            ],
            []  # Responses query
        ]

        result = repo.get_by_project(1)

        assert len(result) == 1
        assert result[0].text == "Test remark"

    def test_get_by_project_with_status(self, repo, mock_db):
        """Test getting remarks for a project with status filter."""
        mock_db.fetch_all.side_effect = [[], []]

        result = repo.get_by_project(1, status="open")

        assert result == []

    def test_get_by_project_paginated(self, repo, mock_db):
        """Test getting remarks with pagination."""
        mock_db.fetch_all.return_value = []
        mock_db.fetch_one.return_value = {"cnt": 0}

        result, total = repo.get_by_project_paginated(1, limit=10, offset=0)

        assert result == []
        assert total == 0

    def test_get_responses(self, repo, mock_db):
        """Test getting responses for a remark."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "remark_id": 1, "author_id": 2, "author_name": "Responder",
                "text": "Response text", "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc)
            }
        ]

        result = repo.get_responses(1)

        assert len(result) == 1
        assert result[0].text == "Response text"

    def test_create(self, repo, mock_db):
        """Test creating a new remark."""
        mock_db.fetch_one.return_value = {
            "id": 1, "project_id": 1, "document_id": None, "revision_id": None,
            "author_id": 1, "author_name": "Author", "assignee_id": None, "assignee_name": "Assignee",
            "source": "internal", "text": "New remark", "status": "open", "resolution_comment": None,
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc), "resolved_at": None
        }

        result = repo.create(1, "New remark", 1, document_id=None, assignee_id=None, source="internal")

        assert result is not None
        assert result.text == "New remark"
        assert result.status == "open"

    def test_update_status(self, repo, mock_db):
        """Test updating remark status."""
        mock_db.execute.return_value = None
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "project_id": 1, "document_id": None, "revision_id": None,
                "author_id": 1, "author_name": "Author", "assignee_id": None, "assignee_name": None,
                "source": "internal", "text": "Test remark", "status": "resolved", "resolution_comment": "Fixed",
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
                "resolved_at": datetime(2026, 1, 15, tzinfo=timezone.utc)
            }
        ]

        result = repo.update_status(1, "resolved", "Fixed")

        assert result is not None
        assert result.status == "resolved"

    def test_update_status_to_open(self, repo, mock_db):
        """Test updating remark status to open."""
        mock_db.execute.return_value = None
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "project_id": 1, "document_id": None, "revision_id": None,
                "author_id": 1, "author_name": "Author", "assignee_id": None, "assignee_name": None,
                "source": "internal", "text": "Test remark", "status": "open", "resolution_comment": None,
                "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc), "resolved_at": None
            }
        ]

        result = repo.update_status(1, "open", None)

        assert result is not None
        assert result.status == "open"
        assert result.resolved_at is None

    def test_add_response(self, repo, mock_db):
        """Test adding a response to a remark."""
        mock_db.fetch_one.return_value = {
            "id": 1, "remark_id": 1, "author_id": 2, "author_name": "Responder",
            "text": "Response text", "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc)
        }

        result = repo.add_response(1, 2, "Response text")

        assert result is not None
        assert result.text == "Response text"
