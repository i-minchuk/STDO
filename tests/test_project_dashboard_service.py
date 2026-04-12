"""Tests for ProjectDashboardService."""
import os
import pytest
from unittest.mock import MagicMock
from datetime import date

# Disable cache for testing to ensure fresh data on each call
os.environ["DISABLE_CACHE"] = "true"


class TestProjectDashboardService:
    """Tests for ProjectDashboardService business logic."""

    @pytest.fixture
    def mock_project_repo(self):
        """Create a mock project repository."""
        return MagicMock()

    @pytest.fixture
    def mock_task_repo(self):
        """Create a mock task repository."""
        return MagicMock()

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_project_repo, mock_task_repo, mock_db):
        """Create ProjectDashboardService with mocked dependencies."""
        from services.project_dashboard_service import ProjectDashboardService
        return ProjectDashboardService(
            project_repo=mock_project_repo,
            task_repo=mock_task_repo,
            db=mock_db,
        )

    def test_get_portfolio_today_overview_empty(self, service, mock_project_repo):
        """Test portfolio overview with no projects."""
        mock_project_repo.list_all.return_value = []
        target_date = date(2026, 1, 15)

        result = service.get_portfolio_today_overview_dto(target_date)

        assert result.projects == []
        assert result.portfolio_summary.projects_total == 0

    def test_get_portfolio_today_overview_with_projects(self, service, mock_project_repo, mock_task_repo, mock_db):
        """Test portfolio overview with active projects."""
        from models.project import Project
        from models.planned_task import PlannedTask
        from models.enums import ProjectStatus, TaskType, TaskStatus

        mock_project = Project(
            id=1, code="PRJ-001", name="Test Project", customer="Customer",
            status=ProjectStatus.ACTIVE, manager_id=1, start_date=date(2026, 1, 1),
            end_date_planned=date(2026, 12, 31), end_date_forecast=None,
            end_date_actual=None, created_at=date(2026, 1, 1),
            custom_fields={}, vdr_required=False, otk_required=False,
            crs_deadline_days=3, logistics_delivery_weeks=2, logistics_complexity="normal"
        )
        mock_project_repo.list_all.return_value = [mock_project]

        # Setup mock for optimized query (IN clause)
        mock_task = PlannedTask(
            id=1, project_id=1, project_code="PRJ-001", project_name="Test",
            document_id=None, document_code=None, revision_id=None, revision_index=None,
            name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=1,
            owner_name="Engineer", duration_days_planned=5, work_hours_planned=40.0,
            start_date_planned=date(2026, 1, 1), end_date_planned=date(2026, 1, 6),
            start_date_actual=date(2026, 1, 1), end_date_actual=None,
            percent_complete=100, status=TaskStatus.COMPLETED,
            es=0, ef=5, ls=0, lf=5, slack=0, actual_hours=40.0
        )
        
        # Mock fetch_all to return tasks (new optimized approach)
        mock_db.fetch_all = MagicMock(return_value=[{
            "id": 1, "project_id": 1, "project_code": "PRJ-001", "project_name": "Test",
            "document_id": None, "document_code": None, "revision_id": None, "revision_index": None,
            "name": "Task 1", "task_type": "engineering", "assigned_to": 1,
            "owner_name": "Engineer", "duration_days_planned": 5, "work_hours_planned": 40.0,
            "start_date_planned": date(2026, 1, 1), "end_date_planned": date(2026, 1, 6),
            "start_date_actual": date(2026, 1, 1), "end_date_actual": None,
            "percent_complete": 100, "status": "completed",
            "es": 0, "ef": 5, "ls": 0, "lf": 5, "slack": 0, "actual_hours": 40.0
        }])

        result = service.get_portfolio_today_overview_dto(date(2026, 1, 15))

        assert len(result.projects) == 1
        assert result.projects[0].project.id == 1
        assert result.projects[0].health.percent_complete == 100.0

    def test_get_portfolio_skips_completed_projects(self, service, mock_project_repo, mock_db):
        """Test that completed projects are skipped."""
        from models.project import Project
        from models.enums import ProjectStatus

        mock_project = Project(
            id=1, code="PRJ-001", name="Test Project", customer="Customer",
            status=ProjectStatus.COMPLETED, manager_id=1, start_date=date(2025, 1, 1),
            end_date_planned=date(2025, 12, 31), end_date_forecast=None,
            end_date_actual=date(2025, 12, 30), created_at=date(2025, 1, 1),
            custom_fields={}, vdr_required=False, otk_required=False,
            crs_deadline_days=3, logistics_delivery_weeks=2, logistics_complexity="normal"
        )
        mock_project_repo.list_all.return_value = [mock_project]
        mock_db.fetch_all = MagicMock(return_value=[])

        result = service.get_portfolio_today_overview_dto(date(2026, 1, 15))

        assert result.projects == []

    def test_recalculate_project_metrics_no_tasks(self, service):
        """Test recalculation with no tasks."""
        result = service.recalculate_project_metrics(1)

        assert result["total"] == 0
        assert result["spi"] == 1.0
        assert result["cpi"] == 1.0
        assert result["risk_level"] == "low"

    def test_recalculate_project_metrics_with_tasks(self, service, mock_task_repo):
        """Test recalculation with tasks."""
        from models.planned_task import PlannedTask
        from models.enums import TaskType, TaskStatus

        tasks = [
            PlannedTask(
                id=1, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=1,
                owner_name="Engineer", duration_days_planned=5, work_hours_planned=40.0,
                start_date_planned=date(2026, 1, 1), end_date_planned=date(2026, 1, 6),
                start_date_actual=date(2026, 1, 1), end_date_actual=None,
                percent_complete=100, status=TaskStatus.COMPLETED,
                es=0, ef=5, ls=0, lf=5, slack=0, actual_hours=40.0
            ),
            PlannedTask(
                id=2, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 2", task_type=TaskType.REVIEW, assigned_to=2,
                owner_name="Reviewer", duration_days_planned=3, work_hours_planned=24.0,
                start_date_planned=date(2026, 1, 6), end_date_planned=date(2026, 1, 9),
                start_date_actual=None, end_date_actual=None,
                percent_complete=0, status=TaskStatus.NOT_STARTED,
                es=None, ef=None, ls=None, lf=None, slack=None, actual_hours=None
            ),
        ]
        mock_task_repo.get_by_project_id.return_value = tasks

        result = service.recalculate_project_metrics(1)

        assert result["total"] == 2
        assert result["completed"] == 1
        assert result["in_progress"] == 0
        assert result["not_started"] == 1
        assert result["spi"] == 0.5
        assert result["cpi"] == 0.625  # 40 / (40 + 24)

    def test_recalculate_project_metrics_critical_tasks(self, service, mock_task_repo):
        """Test recalculation counts critical tasks."""
        from models.planned_task import PlannedTask
        from models.enums import TaskType, TaskStatus

        tasks = [
            PlannedTask(
                id=1, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=1,
                owner_name="Engineer", duration_days_planned=5, work_hours_planned=40.0,
                start_date_planned=date(2026, 1, 1), end_date_planned=date(2026, 1, 6),
                start_date_actual=date(2026, 1, 1), end_date_actual=None,
                percent_complete=50, status=TaskStatus.IN_PROGRESS,
                es=0, ef=5, ls=0, lf=5, slack=0, actual_hours=20.0
            ),
            PlannedTask(
                id=2, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 2", task_type=TaskType.REVIEW, assigned_to=2,
                owner_name="Reviewer", duration_days_planned=3, work_hours_planned=24.0,
                start_date_planned=date(2026, 1, 6), end_date_planned=date(2026, 1, 9),
                start_date_actual=None, end_date_actual=None,
                percent_complete=0, status=TaskStatus.NOT_STARTED,
                es=5, ef=8, ls=7, lf=10, slack=2, actual_hours=None
            ),
        ]
        mock_task_repo.get_by_project_id.return_value = tasks

        result = service.recalculate_project_metrics(1)

        assert result["critical_tasks"] == 1  # Only task 1 has slack=0

    def test_recalculate_project_metrics_overdue_tasks(self, service, mock_task_repo):
        """Test recalculation counts overdue tasks."""
        from models.planned_task import PlannedTask
        from models.enums import TaskType, TaskStatus

        tasks = [
            PlannedTask(
                id=1, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=1,
                owner_name="Engineer", duration_days_planned=5, work_hours_planned=40.0,
                start_date_planned=date(2025, 12, 1), end_date_planned=date(2025, 12, 6),
                start_date_actual=date(2025, 12, 1), end_date_actual=None,
                percent_complete=50, status=TaskStatus.IN_PROGRESS,
                es=0, ef=5, ls=0, lf=5, slack=0, actual_hours=20.0
            ),
        ]
        mock_task_repo.get_by_project_id.return_value = tasks

        result = service.recalculate_project_metrics(1)

        # Task is overdue (end_date_planned < today and not completed)
        assert result["overdue_tasks"] == 1

    def test_get_latest_metrics_no_db(self, service):
        """Test getting latest metrics without DB connection."""
        service._db = None

        result = service.get_latest_metrics(1)

        assert result is None

    def test_get_latest_metrics_with_db(self, service, mock_db):
        """Test getting latest metrics with DB."""
        mock_db.fetch_one.return_value = {
            "project_id": 1,
            "calculated_at": date(2026, 1, 15),
            "total_tasks": 10,
            "completed_tasks": 5,
            "in_progress_tasks": 2,
            "blocked_tasks": 1,
            "not_started_tasks": 2,
            "spi": 0.5,
            "cpi": 0.8,
            "risk_level": "medium",
            "critical_tasks": 3,
            "overdue_tasks": 1,
            "total_planned_hours": 100.0,
            "completed_hours": 50.0,
        }

        result = service.get_latest_metrics(1)

        assert result is not None
        assert result["total_tasks"] == 10
        assert result["spi"] == 0.5
