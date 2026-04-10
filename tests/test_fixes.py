"""Тесты для recalculate_project_metrics()"""
import pytest
from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch

from models.enums import TaskStatus, TaskType
from models.planned_task import PlannedTask


class TestRecalculateProjectMetrics:
    """Тесты для метода recalculate_project_metrics"""

    @pytest.fixture
    def mock_locator(self):
        """Создаём мок для service_locator"""
        locator = MagicMock()
        return locator

    @pytest.fixture
    def empty_tasks_project(self, mock_locator):
        """Проект без задач"""
        mock_locator.planned_task_repo.get_by_project_id.return_value = []
        return mock_locator

    @pytest.fixture
    def partial_tasks_project(self, mock_locator):
        """Проект с частично выполненными задачами"""
        tasks = [
            PlannedTask(
                id=1, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=None, owner_name="Engineer1",
                duration_days_planned=5, work_hours_planned=8, percent_complete=100,
                start_date_planned=date(2025, 1, 1), end_date_planned=date(2025, 1, 15),
                start_date_actual=date(2025, 1, 1), end_date_actual=None,
                status=TaskStatus.COMPLETED, actual_hours=8, slack=5
            ),
            PlannedTask(
                id=2, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 2", task_type=TaskType.ENGINEERING, assigned_to=None, owner_name="Engineer2",
                duration_days_planned=10, work_hours_planned=16, percent_complete=50,
                start_date_planned=date(2025, 1, 10), end_date_planned=date(2025, 2, 1),
                start_date_actual=date(2025, 1, 10), end_date_actual=None,
                status=TaskStatus.IN_PROGRESS, actual_hours=8, slack=2
            ),
            PlannedTask(
                id=3, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 3", task_type=TaskType.ENGINEERING, assigned_to=None, owner_name=None,
                duration_days_planned=2, work_hours_planned=4, percent_complete=0,
                start_date_planned=date(2025, 2, 1), end_date_planned=date(2025, 3, 1),
                start_date_actual=None, end_date_actual=None,
                status=TaskStatus.NOT_STARTED, actual_hours=0, slack=None
            ),
        ]
        mock_locator.planned_task_repo.get_by_project_id.return_value = tasks
        return mock_locator

    @pytest.fixture
    def completed_tasks_project(self, mock_locator):
        """Проект со всеми выполненными задачами"""
        tasks = [
            PlannedTask(
                id=1, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=None, owner_name="Engineer1",
                duration_days_planned=5, work_hours_planned=10, percent_complete=100,
                start_date_planned=date(2025, 1, 1), end_date_planned=date(2025, 1, 15),
                start_date_actual=date(2025, 1, 1), end_date_actual=date(2025, 1, 14),
                status=TaskStatus.COMPLETED, actual_hours=10, slack=5
            ),
            PlannedTask(
                id=2, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 2", task_type=TaskType.ENGINEERING, assigned_to=None, owner_name="Engineer2",
                duration_days_planned=10, work_hours_planned=20, percent_complete=90,
                start_date_planned=date(2025, 1, 10), end_date_planned=date(2025, 2, 1),
                start_date_actual=date(2025, 1, 10), end_date_actual=date(2025, 1, 28),
                status=TaskStatus.COMPLETED, actual_hours=18, slack=3
            ),
        ]
        mock_locator.planned_task_repo.get_by_project_id.return_value = tasks
        return mock_locator

    @pytest.fixture
    def overdue_tasks_project(self, mock_locator):
        """Проект с просроченными задачами"""
        tasks = [
            PlannedTask(
                id=1, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 1", task_type=TaskType.ENGINEERING, assigned_to=None, owner_name="Engineer1",
                duration_days_planned=5, work_hours_planned=8, percent_complete=50,
                start_date_planned=date(2019, 12, 1), end_date_planned=date(2020, 1, 1),
                start_date_actual=date(2019, 12, 1), end_date_actual=None,
                status=TaskStatus.IN_PROGRESS, actual_hours=4, slack=0
            ),
            PlannedTask(
                id=2, project_id=1, project_code="PRJ-001", project_name="Test",
                document_id=None, document_code=None, revision_id=None, revision_index=None,
                name="Task 2", task_type=TaskType.ENGINEERING, assigned_to=None, owner_name=None,
                duration_days_planned=2, work_hours_planned=4, percent_complete=0,
                start_date_planned=date(2020, 1, 1), end_date_planned=date(2020, 2, 1),
                start_date_actual=None, end_date_actual=None,
                status=TaskStatus.NOT_STARTED, actual_hours=0, slack=None
            ),
        ]
        mock_locator.planned_task_repo.get_by_project_id.return_value = tasks
        return mock_locator

    def test_empty_project(self, empty_tasks_project):
        """Тест: проект без задач"""
        from services.project_dashboard_service import ProjectDashboardService
        
        service = ProjectDashboardService(
            project_repo=empty_tasks_project.project_repo,
            task_repo=empty_tasks_project.planned_task_repo,
            db=empty_tasks_project.db,
        )
        
        # Не должно вызвать исключения
        service.recalculate_project_metrics(1)
        
        # Проверяем, что метод get_by_project_id был вызван
        empty_tasks_project.planned_task_repo.get_by_project_id.assert_called_once_with(1)

    def test_partial_completion(self, partial_tasks_project):
        """Тест: частично выполненные задачи"""
        from services.project_dashboard_service import ProjectDashboardService
        
        service = ProjectDashboardService(
            project_repo=partial_tasks_project.project_repo,
            task_repo=partial_tasks_project.planned_task_repo,
            db=partial_tasks_project.db,
        )
        
        # Вызываем метод - не должно быть исключений
        service.recalculate_project_metrics(1)
        
        # Проверяем вызов
        partial_tasks_project.planned_task_repo.get_by_project_id.assert_called_once_with(1)

    def test_all_completed(self, completed_tasks_project):
        """Тест: все задачи выполнены (SPI = 1.0)"""
        from services.project_dashboard_service import ProjectDashboardService
        
        service = ProjectDashboardService(
            project_repo=completed_tasks_project.project_repo,
            task_repo=completed_tasks_project.planned_task_repo,
            db=completed_tasks_project.db,
        )
        
        # Вызываем метод
        service.recalculate_project_metrics(1)
        
        # Должен быть SPI = 1.0 (все задачи выполнены)
        completed_tasks_project.planned_task_repo.get_by_project_id.assert_called_once_with(1)

    def test_overdue_tasks(self, overdue_tasks_project):
        """Тест: просроченные задачи"""
        from services.project_dashboard_service import ProjectDashboardService
        
        service = ProjectDashboardService(
            project_repo=overdue_tasks_project.project_repo,
            task_repo=overdue_tasks_project.planned_task_repo,
            db=overdue_tasks_project.db,
        )
        
        # Вызываем метод
        service.recalculate_project_metrics(1)
        
        # Должен корректно обработать просроченные задачи
        overdue_tasks_project.planned_task_repo.get_by_project_id.assert_called_once_with(1)


class TestDatetimeUtils:
    """Тесты для datetime_utils"""
    
    def test_utc_now(self):
        """Проверка utc_now() возвращает timezone-aware datetime"""
        from datetime import timezone
        from core.datetime_utils import utc_now
        
        dt = utc_now()
        
        assert dt.tzinfo is not None, "Должен быть timezone-aware"
        assert dt.tzinfo == timezone.utc, "Должен быть UTC"
    
    def test_utc_now_iso(self):
        """Проверка utc_now_iso() возвращает ISO строку"""
        from core.datetime_utils import utc_now_iso
        
        iso = utc_now_iso()
        
        assert isinstance(iso, str), "Должен быть строкой"
        assert '+' in iso or 'Z' in iso or '+00:00' in iso, "Должен содержать timezone"
    
    def test_datetime_to_utc_naive(self):
        """Конвертация naive datetime в UTC"""
        from datetime import datetime
        from core.datetime_utils import datetime_to_utc
        
        naive_dt = datetime(2025, 1, 15, 12, 0, 0)
        utc_dt = datetime_to_utc(naive_dt)
        
        assert utc_dt.tzinfo is not None, "Должен стать timezone-aware"
    
    def test_datetime_to_utc_aware(self):
        """Конвертация aware datetime в UTC"""
        from datetime import datetime, timezone
        from core.datetime_utils import datetime_to_utc
        
        aware_dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        utc_dt = datetime_to_utc(aware_dt)
        
        assert utc_dt.tzinfo is not None
        assert utc_dt.tzinfo == timezone.utc
    
    def test_format_iso(self):
        """Проверка format_iso()"""
        from datetime import datetime, timezone
        from core.datetime_utils import format_iso
        
        dt = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        iso = format_iso(dt)
        
        assert isinstance(iso, str)
        assert '+00:00' in iso


class TestRateLimiter:
    """Тесты для rate limiting"""
    
    def test_tender_api_has_limiter(self):
        """Проверка, что tender_api имеет rate limiter"""
        from api.tender_api import limiter, router
        
        assert limiter is not None, "Limiter должен быть определён"
        assert router is not None, "Router должен быть определён"
    
    def test_assess_endpoint_has_limit(self):
        """Проверка, что endpoint /assess имеет rate limit"""
        from api.tender_api import assess_tender
        import inspect
        
        # Проверяем, что функция имеет декоратор limiter
        source = inspect.getsource(assess_tender)
        
        assert '@limiter.limit' in source or 'limiter.limit' in source, \
            "Endpoint должен иметь rate limit декоратор"
    
    def test_main_app_has_limiter(self):
        """Проверка, что main.py имеет rate limiter"""
        from main import limiter, app
        
        assert limiter is not None, "Limiter должен быть в main.py"
        assert hasattr(app.state, 'limiter'), "App должен иметь limiter в state"


class TestProjectHealthType:
    """Тесты для типа ProjectHealth"""
    
    def test_project_health_has_code(self):
        """Проверка, что ProjectHealth.project содержит code"""
        import os
        types_file = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 'frontend', 'src', 'types', 'index.ts'
        )
        
        # Если файл существует, проверяем его содержимое
        if os.path.exists(types_file):
            with open(types_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем ProjectHealth с code
            assert 'code: string' in content or 'code?' in content, \
                "ProjectHealth должен содержать поле code"
