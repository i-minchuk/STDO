"""Tests for ProjectRepository."""
import pytest
from unittest.mock import MagicMock
from datetime import date
from models.enums import ProjectStatus


class TestProjectRepository:
    """Tests for ProjectRepository."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return MagicMock()

    @pytest.fixture
    def repo(self, mock_db):
        """Create ProjectRepository with mocked database."""
        from repositories.project_repository import ProjectRepository
        return ProjectRepository(db=mock_db)

    def test_get_by_id(self, repo, mock_db):
        """Test retrieving a project by ID."""
        mock_db.fetch_one.return_value = {
            "id": 1, "code": "PRJ-001", "name": "Test Project",
            "customer": "Customer", "status": "active",
            "manager_id": 1, "start_date": date(2026, 1, 1),
            "end_date_planned": date(2026, 12, 31),
            "end_date_forecast": None, "end_date_actual": None,
            "created_at": date(2026, 1, 1), "custom_fields": "{}",
            "vdr_required": False, "otk_required": False,
            "crs_deadline_days": 3, "logistics_delivery_weeks": 2,
            "logistics_complexity": "normal"
        }

        result = repo.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.code == "PRJ-001"
        mock_db.fetch_one.assert_called_once()

    def test_get_by_id_not_found(self, repo, mock_db):
        """Test retrieving a non-existent project."""
        mock_db.fetch_one.return_value = None

        result = repo.get_by_id(999)

        assert result is None

    def test_list_all(self, repo, mock_db):
        """Test listing all projects."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "code": "PRJ-001", "name": "Project 1",
                "customer": "C1", "status": "active", "manager_id": 1,
                "start_date": date(2026, 1, 1), "end_date_planned": date(2026, 12, 31),
                "end_date_forecast": None, "end_date_actual": None,
                "created_at": date(2026, 1, 1), "custom_fields": "{}",
                "vdr_required": False, "otk_required": False,
                "crs_deadline_days": 3, "logistics_delivery_weeks": 2,
                "logistics_complexity": "normal"
            }
        ]

        result = repo.list_all()

        assert len(result) == 1
        assert result[0].name == "Project 1"
        # Verify order_by="name" was used
        call_args = mock_db.fetch_all.call_args
        assert "ORDER BY name" in call_args[0][0]

    def test_list_all_paginated(self, repo, mock_db):
        """Test listing projects with pagination."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "code": "PRJ-001", "name": "Project 1",
                "customer": "C1", "status": "active", "manager_id": 1,
                "start_date": date(2026, 1, 1), "end_date_planned": date(2026, 12, 31),
                "end_date_forecast": None, "end_date_actual": None,
                "created_at": date(2026, 1, 1), "custom_fields": "{}",
                "vdr_required": False, "otk_required": False,
                "crs_deadline_days": 3, "logistics_delivery_weeks": 2,
                "logistics_complexity": "normal"
            }
        ]
        mock_db.fetch_one.return_value = {"cnt": 1}

        result, total = repo.list_all_paginated(limit=10, offset=0)

        assert len(result) == 1
        assert total == 1

    def test_insert(self, repo, mock_db):
        """Test inserting a new project."""
        mock_db.fetch_one.return_value = {
            "id": 2, "code": "PRJ-002", "name": "New Project",
            "customer": "Customer", "status": "planned",
            "manager_id": None, "start_date": None,
            "end_date_planned": None, "end_date_forecast": None,
            "end_date_actual": None, "created_at": date(2026, 1, 1),
            "custom_fields": "{}", "vdr_required": False,
            "otk_required": False, "crs_deadline_days": 3,
            "logistics_delivery_weeks": 2, "logistics_complexity": "normal"
        }

        result = repo.insert(
            code="PRJ-002", name="New Project", customer="Customer",
            status=ProjectStatus.PLANNED, manager_id=None,
            start_date=None, end_date_planned=None
        )

        assert result is not None
        assert result.id == 2
        mock_db.fetch_one.assert_called_once()

    def test_update_status(self, repo, mock_db):
        """Test updating project status."""
        repo.update_status(1, ProjectStatus.COMPLETED)

        mock_db.execute.assert_called_once()

    def test_update_status_with_end_date(self, repo, mock_db):
        """Test updating project status with end date."""
        end_date = date(2026, 12, 31)
        repo.update_status(1, ProjectStatus.COMPLETED, end_date_actual=end_date)

        mock_db.execute.assert_called_once()

    def test_count_by_status(self, repo, mock_db):
        """Test counting projects by status."""
        mock_db.fetch_one.return_value = {"cnt": 5}

        result = repo.count_by_status(ProjectStatus.ACTIVE)

        assert result == 5
        mock_db.fetch_one.assert_called_once()
