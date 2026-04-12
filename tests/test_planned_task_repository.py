"""Tests for PlannedTaskRepository."""
import pytest
from unittest.mock import MagicMock
from datetime import date
from models.enums import TaskStatus, TaskType


class TestPlannedTaskRepository:
    """Tests for PlannedTaskRepository."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return MagicMock()

    @pytest.fixture
    def repo(self, mock_db):
        """Create PlannedTaskRepository with mocked database."""
        from repositories.planned_task_repository import PlannedTaskRepository
        return PlannedTaskRepository(db=mock_db)

    def test_get_by_id(self, repo, mock_db):
        """Test retrieving a task by ID."""
        mock_db.fetch_one.return_value = {
            "id": 1, "project_id": 1, "project_code": "PRJ-001",
            "project_name": "Test Project", "document_id": None,
            "document_code": None, "revision_id": None, "revision_index": None,
            "name": "Task 1", "task_type": "engineering", "assigned_to": None,
            "owner_name": "Engineer", "duration_days_planned": 5,
            "work_hours_planned": 40.0, "start_date_planned": date(2026, 1, 1),
            "end_date_planned": date(2026, 1, 10), "start_date_actual": None,
            "end_date_actual": None, "percent_complete": 0, "status": "not_started",
            "es": None, "ef": None, "ls": None, "lf": None, "slack": None,
            "actual_hours": None
        }

        result = repo.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Task 1"

    def test_get_by_id_not_found(self, repo, mock_db):
        """Test retrieving a non-existent task."""
        mock_db.fetch_one.return_value = None

        result = repo.get_by_id(999)

        assert result is None

    def test_get_by_project_id(self, repo, mock_db):
        """Test retrieving tasks for a project."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "project_id": 1, "project_code": "PRJ-001",
                "project_name": "Test Project", "document_id": None,
                "document_code": None, "revision_id": None, "revision_index": None,
                "name": "Task 1", "task_type": "engineering", "assigned_to": None,
                "owner_name": "Engineer", "duration_days_planned": 5,
                "work_hours_planned": 40.0, "start_date_planned": date(2026, 1, 1),
                "end_date_planned": date(2026, 1, 10), "start_date_actual": None,
                "end_date_actual": None, "percent_complete": 0, "status": "not_started",
                "es": None, "ef": None, "ls": None, "lf": None, "slack": None,
                "actual_hours": None
            }
        ]

        result = repo.get_by_project_id(1)

        assert len(result) == 1
        assert result[0].project_id == 1

    def test_get_all(self, repo, mock_db):
        """Test retrieving all tasks."""
        mock_db.fetch_all.return_value = []

        result = repo.get_all()

        assert result == []

    def test_get_all_paginated(self, repo, mock_db):
        """Test retrieving tasks with pagination."""
        mock_db.fetch_all.return_value = []
        mock_db.fetch_one.return_value = {"cnt": 0}

        result, total = repo.get_all_paginated(limit=10, offset=0)

        assert result == []
        assert total == 0

    def test_get_by_revision_id(self, repo, mock_db):
        """Test retrieving tasks for a revision."""
        mock_db.fetch_all.return_value = []

        result = repo.get_by_revision_id(1)

        assert result == []

    def test_insert(self, repo, mock_db):
        """Test inserting a new task."""
        mock_db.fetch_one.return_value = {
            "id": 2, "project_id": 1, "project_code": "PRJ-001",
            "project_name": "Test Project", "document_id": None,
            "document_code": None, "revision_id": None, "revision_index": None,
            "name": "New Task", "task_type": "engineering", "assigned_to": None,
            "owner_name": "Engineer", "duration_days_planned": 5,
            "work_hours_planned": 40.0, "start_date_planned": date(2026, 1, 1),
            "end_date_planned": date(2026, 1, 10), "start_date_actual": None,
            "end_date_actual": None, "percent_complete": 0, "status": "not_started",
            "es": None, "ef": None, "ls": None, "lf": None, "slack": None,
            "actual_hours": None
        }

        result = repo.insert(
            project_id=1, project_code="PRJ-001", project_name="Test Project",
            document_id=None, document_code=None, revision_id=None,
            revision_index=None, name="New Task", task_type=TaskType.ENGINEERING,
            assigned_to=None, owner_name="Engineer", duration_days_planned=5,
            work_hours_planned=40.0, start_date_planned=date(2026, 1, 1),
            end_date_planned=date(2026, 1, 10), status=TaskStatus.NOT_STARTED
        )

        assert result is not None
        assert result.id == 2

    def test_update_progress(self, repo, mock_db):
        """Test updating task progress."""
        repo.update_progress(
            task_id=1, percent_complete=50,
            start_date_actual=date(2026, 1, 1),
            end_date_actual=None, actual_hours=20.0,
            status=TaskStatus.IN_PROGRESS
        )

        mock_db.execute.assert_called_once()

    def test_count_by_project_and_status(self, repo, mock_db):
        """Test counting tasks by project and status."""
        mock_db.fetch_one.return_value = {"cnt": 3}

        result = repo.count_by_project_and_status(1, TaskStatus.COMPLETED)

        assert result == 3

    def test_count_by_project(self, repo, mock_db):
        """Test counting tasks by project."""
        mock_db.fetch_one.return_value = {"cnt": 10}

        result = repo.count_by_project(1)

        assert result == 10
