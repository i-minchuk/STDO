"""Tests for TaskDependencyRepository."""
import pytest
from unittest.mock import MagicMock


class TestTaskDependencyRepository:
    """Tests for TaskDependencyRepository."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return MagicMock()

    @pytest.fixture
    def repo(self, mock_db):
        """Create TaskDependencyRepository with mocked database."""
        from repositories.task_dependency_repository import TaskDependencyRepository
        return TaskDependencyRepository(db=mock_db)

    def test_get_by_id(self, repo, mock_db):
        """Test retrieving a dependency by ID."""
        mock_db.fetch_one.return_value = {
            "id": 1, "project_id": 1, "predecessor_task_id": 1,
            "successor_task_id": 2, "dependency_type": "FS", "lag_days": 0
        }

        result = repo.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.dependency_type == "FS"

    def test_get_by_id_not_found(self, repo, mock_db):
        """Test retrieving a non-existent dependency."""
        mock_db.fetch_one.return_value = None

        result = repo.get_by_id(999)

        assert result is None

    def test_get_for_project(self, repo, mock_db):
        """Test getting dependencies for a project."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "project_id": 1, "predecessor_task_id": 1,
                "successor_task_id": 2, "dependency_type": "FS", "lag_days": 0
            }
        ]

        result = repo.get_for_project(1)

        assert len(result) == 1
        assert result[0].project_id == 1

    def test_get_for_task(self, repo, mock_db):
        """Test getting dependencies for a task."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "project_id": 1, "predecessor_task_id": 1,
                "successor_task_id": 2, "dependency_type": "FS", "lag_days": 0
            }
        ]

        result = repo.get_for_task(1)

        assert len(result) == 1

    def test_insert(self, repo, mock_db):
        """Test inserting a new dependency."""
        mock_db.fetch_one.return_value = {
            "id": 1, "project_id": 1, "predecessor_task_id": 1,
            "successor_task_id": 2, "dependency_type": "FS", "lag_days": 0
        }

        result = repo.insert(1, 1, 2, "FS", 0)

        assert result is not None
        assert result.dependency_type == "FS"

    def test_insert_with_lag(self, repo, mock_db):
        """Test inserting a dependency with lag days."""
        mock_db.fetch_one.return_value = {
            "id": 1, "project_id": 1, "predecessor_task_id": 1,
            "successor_task_id": 2, "dependency_type": "FS", "lag_days": 2
        }

        result = repo.insert(1, 1, 2, "FS", 2)

        assert result is not None
        assert result.lag_days == 2

    def test_delete_for_task(self, repo, mock_db):
        """Test deleting dependencies for a task."""
        mock_db.execute.return_value = 1

        repo.delete_for_task(1)

        mock_db.execute.assert_called_once()

    def test_delete_between(self, repo, mock_db):
        """Test deleting a specific dependency."""
        mock_db.execute.return_value = 1

        repo.delete_between(1, 2)

        mock_db.execute.assert_called_once()
