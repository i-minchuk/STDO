"""Tests for HeatmapService."""
import pytest
from unittest.mock import MagicMock
from datetime import date


class TestHeatmapService:
    """Tests for HeatmapService business logic."""

    @pytest.fixture
    def mock_time_log_repo(self):
        """Create a mock time log repository."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_time_log_repo):
        """Create HeatmapService with mocked dependencies."""
        from services.heatmap_service import HeatmapService
        return HeatmapService(time_log_repo=mock_time_log_repo)

    def test_generate_weekly_heatmap(self, service, mock_time_log_repo):
        """Test generating weekly heatmap."""
        from models.time_log import TimeLog

        mock_log1 = MagicMock()
        mock_log1.day = date(2026, 1, 5)  # Monday
        mock_log1.hours = 8.0

        mock_log2 = MagicMock()
        mock_log2.day = date(2026, 1, 6)  # Tuesday
        mock_log2.hours = 6.0

        mock_time_log_repo.get_by_user_id.return_value = [mock_log1, mock_log2]

        result = service.generate_weekly_heatmap(user_id=1, weeks=12)

        assert "2026-W02" in result
        assert result["2026-W02"]["Mon"] == 8.0
        assert result["2026-W02"]["Tue"] == 6.0

    def test_generate_weekly_heatmap_empty(self, service, mock_time_log_repo):
        """Test generating weekly heatmap with no logs."""
        mock_time_log_repo.get_by_user_id.return_value = []

        result = service.generate_weekly_heatmap(user_id=1, weeks=12)

        assert result == {}

    def test_generate_monthly_heatmap(self, service, mock_time_log_repo):
        """Test generating monthly heatmap."""
        from models.time_log import TimeLog

        mock_log1 = MagicMock()
        mock_log1.day = date(2026, 1, 5)
        mock_log1.hours = 40.0

        mock_log2 = MagicMock()
        mock_log2.day = date(2026, 1, 12)
        mock_log2.hours = 35.0

        mock_time_log_repo.get_by_user_id.return_value = [mock_log1, mock_log2]

        result = service.generate_monthly_heatmap(user_id=1, months=12)

        assert "2026-01" in result
        assert result["2026-01"] == 75.0

    def test_generate_monthly_heatmap_empty(self, service, mock_time_log_repo):
        """Test generating monthly heatmap with no logs."""
        mock_time_log_repo.get_by_user_id.return_value = []

        result = service.generate_monthly_heatmap(user_id=1, months=12)

        assert result == {}

    def test_get_user_activity_summary(self, service, mock_time_log_repo):
        """Test getting user activity summary."""
        from models.time_log import TimeLog

        mock_log1 = MagicMock()
        mock_log1.day = date(2026, 1, 5)  # Monday
        mock_log1.hours = 8.0

        mock_log2 = MagicMock()
        mock_log2.day = date(2026, 1, 6)  # Tuesday
        mock_log2.hours = 6.0

        mock_log3 = MagicMock()
        mock_log3.day = date(2026, 1, 10)  # Saturday
        mock_log3.hours = 4.0

        mock_time_log_repo.get_by_user_id.return_value = [mock_log1, mock_log2, mock_log3]

        result = service.get_user_activity_summary(user_id=1, days=30)

        assert result["total_hours"] == 18.0
        assert result["work_days"] == 2  # Only Mon, Tue are weekdays
        assert result["avg_daily_hours"] == 9.0
        assert result["total_entries"] == 3

    def test_get_user_activity_summary_no_logs(self, service, mock_time_log_repo):
        """Test getting user activity summary with no logs."""
        mock_time_log_repo.get_by_user_id.return_value = []

        result = service.get_user_activity_summary(user_id=1, days=30)

        assert result["total_hours"] == 0.0
        assert result["work_days"] == 0
        assert result["avg_daily_hours"] == 0.0
        assert result["total_entries"] == 0
