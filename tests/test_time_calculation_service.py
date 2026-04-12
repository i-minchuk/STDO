"""Tests for TimeCalculationService."""
import pytest
from datetime import date
from unittest.mock import MagicMock


class TestTimeCalculationService:
    """Tests for TimeCalculationService business logic."""

    @pytest.fixture
    def mock_work_schedule_repo(self):
        """Create a mock work schedule repository."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_work_schedule_repo):
        """Create TimeCalculationService with mocked dependencies."""
        from services.time_calculation_service import TimeCalculationService
        return TimeCalculationService(work_schedule_repo=mock_work_schedule_repo)

    def test_calculate_work_days_from_hours(self, service):
        """Test calculating work days from hours."""
        from models.work_schedule import WorkSchedule
        mock_schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )
        service._get_schedule_or_fallback = MagicMock(return_value=mock_schedule)

        result = service.calculate_work_days_from_hours(40.0)

        assert result == 5

    def test_calculate_work_days_from_hours_partial(self, service):
        """Test calculating work days from partial hours (rounds up)."""
        from models.work_schedule import WorkSchedule
        mock_schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )
        service._get_schedule_or_fallback = MagicMock(return_value=mock_schedule)

        result = service.calculate_work_days_from_hours(9.0)

        assert result == 2  # 9 hours / 8 hours per day = 1.125 -> rounds up to 2

    def test_calculate_work_days_from_hours_zero(self, service):
        """Test calculating work days from zero hours."""
        result = service.calculate_work_days_from_hours(0)

        assert result == 0

    def test_calculate_work_days_from_hours_negative(self, service):
        """Test calculating work days from negative hours."""
        result = service.calculate_work_days_from_hours(-10)

        assert result == 0

    def test_calculate_hours_from_work_days(self, service):
        """Test calculating work hours from days."""
        from models.work_schedule import WorkSchedule
        mock_schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )
        service._get_schedule_or_fallback = MagicMock(return_value=mock_schedule)

        result = service.calculate_hours_from_work_days(5)

        assert result == 40.0

    def test_calculate_hours_from_work_days_zero(self, service):
        """Test calculating work hours from zero days."""
        result = service.calculate_hours_from_work_days(0)

        assert result == 0

    def test_calculate_hours_from_work_days_negative(self, service):
        """Test calculating work hours from negative days."""
        result = service.calculate_hours_from_work_days(-3)

        assert result == 0

    def test_is_work_day_monday(self, service):
        """Test checking if Monday is a work day."""
        from models.work_schedule import WorkSchedule
        mock_schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )
        service._get_schedule_or_fallback = MagicMock(return_value=mock_schedule)

        monday = date(2026, 1, 5)  # Monday

        assert service.is_work_day(monday) is True

    def test_is_work_day_sunday(self, service):
        """Test checking if Sunday is a work day."""
        from models.work_schedule import WorkSchedule
        mock_schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )
        service._get_schedule_or_fallback = MagicMock(return_value=mock_schedule)

        sunday = date(2026, 1, 4)  # Sunday

        assert service.is_work_day(sunday) is False

    def test_calculate_end_date(self, service):
        """Test calculating end date from start date and work days."""
        from models.work_schedule import WorkSchedule
        mock_schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )
        mock_schedule.is_work_day = lambda wd: wd < 5
        service._get_schedule_or_fallback = MagicMock(return_value=mock_schedule)
        service._work_schedule_repo.add_work_days = MagicMock(
            return_value=date(2026, 1, 10)
        )

        start = date(2026, 1, 5)
        result = service.calculate_end_date(start, 5)

        assert result == date(2026, 1, 10)

    def test_count_work_days_between(self, service):
        """Test counting work days between two dates."""
        from models.work_schedule import WorkSchedule
        mock_schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )
        service._get_schedule_or_fallback = MagicMock(return_value=mock_schedule)
        service._work_schedule_repo.count_work_days = MagicMock(return_value=5)

        start = date(2026, 1, 5)
        end = date(2026, 1, 12)

        result = service.count_work_days_between(start, end)

        assert result == 5

    def test_add_work_days_to_date(self, service):
        """Test adding work days to a date."""
        from models.work_schedule import WorkSchedule
        mock_schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )
        service._get_schedule_or_fallback = MagicMock(return_value=mock_schedule)
        service._work_schedule_repo.add_work_days = MagicMock(
            return_value=date(2026, 1, 15)
        )

        start = date(2026, 1, 5)
        result = service.add_work_days_to_date(start, 10)

        assert result == date(2026, 1, 15)
