"""Tests for remaining fixes: recalculate_project_metrics DB save, model datetime, timezone."""
import pytest
from datetime import datetime, date, timezone
from unittest.mock import MagicMock, patch
import os


class TestRecalculateProjectMetricsWithDB:
    """Tests for recalculate_project_metrics() with DB save."""
    
    def test_returns_metrics_dict(self):
        """recalculate_project_metrics должен возвращать dict с метриками."""
        from services.project_dashboard_service import ProjectDashboardService
        from models.enums import TaskStatus
        
        # Mock repositories
        mock_project_repo = MagicMock()
        mock_task_repo = MagicMock()
        mock_db = MagicMock()
        
        # Create tasks
        tasks = [
            MagicMock(
                id=1, status=TaskStatus.COMPLETED, work_hours_planned=10,
                actual_hours=10, slack=5, end_date_planned=date(2025, 6, 1)
            ),
            MagicMock(
                id=2, status=TaskStatus.IN_PROGRESS, work_hours_planned=20,
                actual_hours=10, slack=2, end_date_planned=date(2025, 7, 1)
            ),
            MagicMock(
                id=3, status=TaskStatus.NOT_STARTED, work_hours_planned=5,
                actual_hours=0, slack=None, end_date_planned=date(2025, 8, 1)
            ),
        ]
        mock_task_repo.get_by_project_id.return_value = tasks
        
        # Create service
        service = ProjectDashboardService(
            project_repo=mock_project_repo,
            task_repo=mock_task_repo,
            db=mock_db,
        )
        
        # Call method
        result = service.recalculate_project_metrics(project_id=1)
        
        # Verify result is dict with metrics
        assert isinstance(result, dict), "Should return dict"
        assert "spi" in result, "Should have spi"
        assert "cpi" in result, "Should have cpi"
        assert "risk_level" in result, "Should have risk_level"
        assert "total" in result, "Should have total"
        assert "completed" in result, "Should have completed"
        
        # Verify values
        assert result["total"] == 3
        assert result["completed"] == 1
        assert result["spi"] == pytest.approx(0.3333, rel=0.01)
        
    def test_saves_to_db_when_db_provided(self):
        """Метрики должны сохраняться в БД если db передан."""
        from services.project_dashboard_service import ProjectDashboardService
        from models.enums import TaskStatus
        
        mock_project_repo = MagicMock()
        mock_task_repo = MagicMock()
        mock_db = MagicMock()
        
        tasks = [
            MagicMock(
                id=1, status=TaskStatus.COMPLETED, work_hours_planned=10,
                actual_hours=10, slack=5, end_date_planned=date(2025, 6, 1)
            ),
        ]
        mock_task_repo.get_by_project_id.return_value = tasks
        
        service = ProjectDashboardService(
            project_repo=mock_project_repo,
            task_repo=mock_task_repo,
            db=mock_db,
        )
        
        service.recalculate_project_metrics(project_id=1)
        
        # Verify DB call was made
        mock_db.fetch_one.assert_called_once()
        call_args = mock_db.fetch_one.call_args
        assert "INSERT INTO project_metrics" in call_args[0][0]
        
    def test_no_db_save_when_db_is_none(self):
        """Метрики НЕ должны сохраняться если db=None (обратная совместимость)."""
        from services.project_dashboard_service import ProjectDashboardService
        from models.enums import TaskStatus
        
        mock_project_repo = MagicMock()
        mock_task_repo = MagicMock()
        
        tasks = [
            MagicMock(
                id=1, status=TaskStatus.COMPLETED, work_hours_planned=10,
                actual_hours=10, slack=5, end_date_planned=date(2025, 6, 1)
            ),
        ]
        mock_task_repo.get_by_project_id.return_value = tasks
        
        # Service without DB
        service = ProjectDashboardService(
            project_repo=mock_project_repo,
            task_repo=mock_task_repo,
            db=None,
        )
        
        # Should not raise, should still return metrics
        result = service.recalculate_project_metrics(project_id=1)
        
        assert isinstance(result, dict)
        assert "spi" in result
        
    def test_get_latest_metrics_returns_data(self):
        """get_latest_metrics должен возвращать данные из БД."""
        from services.project_dashboard_service import ProjectDashboardService
        
        mock_project_repo = MagicMock()
        mock_task_repo = MagicMock()
        mock_db = MagicMock()
        
        # Mock DB response
        mock_db.fetch_one.return_value = {
            "project_id": 1,
            "calculated_at": datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            "total_tasks": 10,
            "completed_tasks": 5,
            "spi": 0.5,
            "cpi": 0.8,
            "risk_level": "high",
            "critical_tasks": 2,
            "overdue_tasks": 3,
        }
        
        service = ProjectDashboardService(
            project_repo=mock_project_repo,
            task_repo=mock_task_repo,
            db=mock_db,
        )
        
        result = service.get_latest_metrics(project_id=1)
        
        assert result is not None
        assert result["project_id"] == 1
        assert result["spi"] == 0.5
        
    def test_get_latest_metrics_returns_none_when_no_data(self):
        """get_latest_metrics должен возвращать None если данных нет."""
        from services.project_dashboard_service import ProjectDashboardService
        
        mock_project_repo = MagicMock()
        mock_task_repo = MagicMock()
        mock_db = MagicMock()
        
        mock_db.fetch_one.return_value = None
        
        service = ProjectDashboardService(
            project_repo=mock_project_repo,
            task_repo=mock_task_repo,
            db=mock_db,
        )
        
        result = service.get_latest_metrics(project_id=999)
        
        assert result is None


class TestModelDatetime:
    """Tests for model datetime with timezone awareness."""
    
    def test_tender_model_uses_utc_now(self):
        """Tender model должен использовать timezone-aware datetime."""
        from models.tender import Tender
        
        # Create tender
        tender = Tender(
            id=1,
            name="Test Tender",
            customer="Customer",
            deadline_date=date.today(),
            status="draft",
        )
        
        # Verify created_at is timezone-aware
        assert tender.created_at.tzinfo is not None, "created_at должен быть timezone-aware"
        # For datetime.timezone.utc, check utc flag
        assert tender.created_at.tzinfo == timezone.utc, "created_at должен быть UTC"
        
    def test_tender_from_row_uses_utc(self):
        """Tender.from_row должен использовать UTC для created_at."""
        from models.tender import Tender
        
        row = {
            "id": 1,
            "name": "Test",
            "customer": "C",
            "deadline_date": date.today(),
            "status": "draft",
            "vdr_required": False,
            "otk_required": False,
            "logistics_complexity": "normal",
            "notes": None,
            "required_disciplines": [],
            "team_size": None,
            "expected_review_rounds": 1,
            "expected_remark_count": 0,
            "created_by": None,
            "created_at": datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),  # Explicit UTC
            "assessed_at": None,
            "assessment_result": None,
        }
        
        tender = Tender.from_row(row)
        
        # Should use utc_now() as fallback
        assert tender.created_at.tzinfo is not None


class TestDatabaseTimezone:
    """Tests for database timezone configuration."""
    
    def test_database_configures_utc_on_connection(self):
        """Database должен устанавливать UTC timezone при подключении."""
        from db.database import Database
        
        # Check that _configure_connection sets timezone
        import inspect
        source = inspect.getsource(Database._configure_connection)
        
        assert "SET TIME ZONE" in source or "TIME ZONE" in source, \
            "Database должен устанавливать timezone"


class TestMigrationExists:
    """Tests for migration file."""
    
    def test_migration_0003_exists(self):
        """Миграция 0003 должна существовать."""
        migration_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 'alembic', 'versions', '0003_add_project_metrics.py'
        )
        
        # Normalize path for Windows
        migration_path = os.path.normpath(migration_path)
        
        assert os.path.exists(migration_path), "Migration 0003 should exist"
        
    def test_migration_creates_project_metrics_table(self):
        """Миграция должна создавать таблицу project_metrics."""
        with open(
            os.path.join(
                os.path.dirname(__file__),
                '..', 'alembic', 'versions', '0003_add_project_metrics.py'
            ),
            'r',
            encoding='utf-8'
        ) as f:
            content = f.read()
        
        assert "project_metrics" in content, "Should reference project_metrics table"
        assert "op.create_table" in content, "Should create table"
        
    def test_migration_sets_postgres_timezone(self):
        """Миграция должна устанавливать PostgreSQL timezone."""
        with open(
            os.path.join(
                os.path.dirname(__file__),
                '..', 'alembic', 'versions', '0003_add_project_metrics.py'
            ),
            'r',
            encoding='utf-8'
        ) as f:
            content = f.read()
        
        assert "TIME ZONE" in content or "timezone" in content.lower(), "Should set timezone"
        assert "UTC" in content, "Should set UTC"


class TestBackwardCompatibility:
    """Tests for backward compatibility."""
    
    def test_project_dashboard_service_works_without_db(self):
        """Service должен работать без db для обратной совместимости."""
        from services.project_dashboard_service import ProjectDashboardService
        
        mock_project_repo = MagicMock()
        mock_task_repo = MagicMock()
        
        # Empty project
        mock_task_repo.get_by_project_id.return_value = []
        
        service = ProjectDashboardService(
            project_repo=mock_project_repo,
            task_repo=mock_task_repo,
        )
        
        # Should not raise
        result = service.recalculate_project_metrics(project_id=1)
        
        assert isinstance(result, dict)
        assert result["total"] == 0
        
    def test_existing_endpoints_still_work(self):
        """Существующие endpoints должны продолжать работать."""
        # Test that we can import all needed modules
        from services.project_dashboard_service import ProjectDashboardService
        from api.internal_project_api import router as internal_router
        from api.project_api import router as project_router
        
        assert internal_router is not None
        assert project_router is not None