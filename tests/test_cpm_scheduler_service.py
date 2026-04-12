"""Tests for CPMSchedulerService."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date


class TestCPMSchedulerService:
    """Tests for CPMSchedulerService business logic."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
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
    def service(self, mock_db, mock_task_repo, mock_dep_repo):
        """Create CPMSchedulerService with mocked dependencies."""
        from services.cpm_scheduler_service import CPMSchedulerService
        return CPMSchedulerService(
            db=mock_db, task_repo=mock_task_repo, dep_repo=mock_dep_repo
        )

    def test_recalculate_with_no_tasks(self, service, mock_task_repo, mock_dep_repo):
        """Test recalculation with no tasks."""
        mock_task_repo.get_by_project_id.return_value = []
        mock_dep_repo.get_for_project.return_value = []

        result = service.recalculate_project_schedule(1)

        assert result == []

    def test_recalculate_single_task(self, service, mock_db, mock_task_repo, mock_dep_repo):
        """Test CPM recalculation with a single task."""
        from models.planned_task import PlannedTask
        from models.enums import TaskType, TaskStatus

        task = PlannedTask(
            id=1, project_id=1, project_code="PRJ-001", project_name="Test",
            document_id=None, document_code=None, revision_id=None, revision_index=None,
            name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=1,
            owner_name="Engineer", duration_days_planned=5, work_hours_planned=40.0,
            start_date_planned=date(2026, 1, 1), end_date_planned=date(2026, 1, 6),
            start_date_actual=None, end_date_actual=None,
            percent_complete=0, status=TaskStatus.NOT_STARTED,
            es=None, ef=None, ls=None, lf=None, slack=None, actual_hours=None
        )
        mock_task_repo.get_by_project_id.return_value = [task]
        mock_dep_repo.get_for_project.return_value = []

        result = service.recalculate_project_schedule(1)

        assert result == [1]
        assert task.es == 0
        assert task.ef == 5
        assert task.ls == 0
        assert task.lf == 5
        assert task.slack == 0

    def test_recalculate_two_tasks_no_dependency(self, service, mock_task_repo, mock_dep_repo):
        """Test CPM with two independent tasks."""
        from models.planned_task import PlannedTask
        from models.enums import TaskType, TaskStatus

        tasks = [
            PlannedTask(
                id=1, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=1,
                owner_name="Engineer", duration_days_planned=5, work_hours_planned=40.0,
                start_date_planned=date(2026, 1, 1), end_date_planned=date(2026, 1, 6),
                start_date_actual=None, end_date_actual=None,
                percent_complete=0, status=TaskStatus.NOT_STARTED,
                es=None, ef=None, ls=None, lf=None, slack=None, actual_hours=None
            ),
            PlannedTask(
                id=2, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 2", task_type=TaskType.REVIEW, assigned_to=2,
                owner_name="Reviewer", duration_days_planned=3, work_hours_planned=24.0,
                start_date_planned=date(2026, 1, 1), end_date_planned=date(2026, 1, 4),
                start_date_actual=None, end_date_actual=None,
                percent_complete=0, status=TaskStatus.NOT_STARTED,
                es=None, ef=None, ls=None, lf=None, slack=None, actual_hours=None
            ),
        ]
        mock_task_repo.get_by_project_id.return_value = tasks
        mock_dep_repo.get_for_project.return_value = []

        result = service.recalculate_project_schedule(1)

        assert len(result) >= 1  # At least one task is critical (slack=0)

    def test_recalculate_with_dependency(self, service, mock_task_repo, mock_dep_repo):
        """Test CPM with task dependency (FS)."""
        from models.planned_task import PlannedTask
        from models.task_dependency import TaskDependency
        from models.enums import TaskType, TaskStatus

        tasks = [
            PlannedTask(
                id=1, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=1,
                owner_name="Engineer", duration_days_planned=5, work_hours_planned=40.0,
                start_date_planned=date(2026, 1, 1), end_date_planned=date(2026, 1, 6),
                start_date_actual=None, end_date_actual=None,
                percent_complete=0, status=TaskStatus.NOT_STARTED,
                es=None, ef=None, ls=None, lf=None, slack=None, actual_hours=None
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
        deps = [
            TaskDependency(
                id=1, project_id=1, predecessor_task_id=1,
                successor_task_id=2, dependency_type="FS", lag_days=0
            )
        ]
        mock_task_repo.get_by_project_id.return_value = tasks
        mock_dep_repo.get_for_project.return_value = deps

        result = service.recalculate_project_schedule(1)

        # Task 1: ES=0, EF=5
        assert tasks[0].es == 0
        assert tasks[0].ef == 5
        # Task 2: ES=5 (after task 1), EF=8
        assert tasks[1].es == 5
        assert tasks[1].ef == 8

    def test_recalculate_with_lag(self, service, mock_task_repo, mock_dep_repo):
        """Test CPM with lag days in dependency."""
        from models.planned_task import PlannedTask
        from models.task_dependency import TaskDependency
        from models.enums import TaskType, TaskStatus

        tasks = [
            PlannedTask(
                id=1, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=1,
                owner_name="Engineer", duration_days_planned=5, work_hours_planned=40.0,
                start_date_planned=date(2026, 1, 1), end_date_planned=date(2026, 1, 6),
                start_date_actual=None, end_date_actual=None,
                percent_complete=0, status=TaskStatus.NOT_STARTED,
                es=None, ef=None, ls=None, lf=None, slack=None, actual_hours=None
            ),
            PlannedTask(
                id=2, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 2", task_type=TaskType.REVIEW, assigned_to=2,
                owner_name="Reviewer", duration_days_planned=3, work_hours_planned=24.0,
                start_date_planned=date(2026, 1, 8), end_date_planned=date(2026, 1, 11),
                start_date_actual=None, end_date_actual=None,
                percent_complete=0, status=TaskStatus.NOT_STARTED,
                es=None, ef=None, ls=None, lf=None, slack=None, actual_hours=None
            ),
        ]
        deps = [
            TaskDependency(
                id=1, project_id=1, predecessor_task_id=1,
                successor_task_id=2, dependency_type="FS", lag_days=2
            )
        ]
        mock_task_repo.get_by_project_id.return_value = tasks
        mock_dep_repo.get_for_project.return_value = deps

        service.recalculate_project_schedule(1)

        # Task 2: ES = EF(task1) + lag = 5 + 2 = 7
        assert tasks[1].es == 7

    def test_recalculate_saves_to_db(self, service, mock_db, mock_task_repo, mock_dep_repo):
        """Test that CPM fields are saved to database."""
        from models.planned_task import PlannedTask
        from models.enums import TaskType, TaskStatus

        task = PlannedTask(
            id=1, project_id=1, project_code="PRJ-001", project_name="Test",
            document_id=None, document_code=None, revision_id=None, revision_index=None,
            name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=1,
            owner_name="Engineer", duration_days_planned=5, work_hours_planned=40.0,
            start_date_planned=date(2026, 1, 1), end_date_planned=date(2026, 1, 6),
            start_date_actual=None, end_date_actual=None,
            percent_complete=0, status=TaskStatus.NOT_STARTED,
            es=None, ef=None, ls=None, lf=None, slack=None, actual_hours=None
        )
        mock_task_repo.get_by_project_id.return_value = [task]
        mock_dep_repo.get_for_project.return_value = []
        mock_db.transaction.return_value.__enter__ = MagicMock()
        mock_db.transaction.return_value.__exit__ = MagicMock()

        service.recalculate_project_schedule(1)

        mock_task_repo.update_cpm_fields.assert_called_once()
        mock_db.transaction.assert_called_once()
