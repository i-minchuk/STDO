"""Tests for WorkScheduleRepository."""
import pytest
from unittest.mock import MagicMock
from datetime import date, datetime


class TestWorkScheduleRepository:
    """Tests for WorkScheduleRepository."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return MagicMock()

    @pytest.fixture
    def repo(self, mock_db):
        """Create WorkScheduleRepository with mocked database."""
        from repositories.work_schedule_repository import WorkScheduleRepository
        return WorkScheduleRepository(db=mock_db)

    def test_get_default_schedule(self, repo, mock_db):
        """Test getting default schedule."""
        mock_db.fetch_one.return_value = {
            "id": 1, "name": "Default", "work_days": [0, 1, 2, 3, 4],
            "start_time_hours": 8.5, "end_time_hours": 17.5,
            "lunch_duration_hours": 1.0, "is_default": True
        }

        result = repo.get_default_schedule()

        assert result is not None
        assert result.name == "Default"

    def test_get_default_schedule_not_found(self, repo, mock_db):
        """Test getting default schedule when none exists."""
        mock_db.fetch_one.return_value = None

        result = repo.get_default_schedule()

        assert result is None

    def test_get_schedule_by_id(self, repo, mock_db):
        """Test getting schedule by ID."""
        mock_db.fetch_one.return_value = {
            "id": 1, "name": "Test Schedule", "work_days": [0, 1, 2, 3, 4],
            "start_time_hours": 8.5, "end_time_hours": 17.5,
            "lunch_duration_hours": 1.0, "is_default": False
        }

        result = repo.get_schedule_by_id(1)

        assert result is not None
        assert result.id == 1

    def test_get_all_schedules(self, repo, mock_db):
        """Test getting all schedules."""
        mock_db.fetch_all.return_value = [
            {
                "id": 1, "name": "Default", "work_days": [0, 1, 2, 3, 4],
                "start_time_hours": 8.5, "end_time_hours": 17.5,
                "lunch_duration_hours": 1.0, "is_default": True
            }
        ]

        result = repo.get_all_schedules()

        assert len(result) == 1

    def test_create_schedule(self, repo, mock_db):
        """Test creating a new schedule."""
        mock_db.fetch_one.return_value = {
            "id": 2, "name": "New Schedule", "work_days": [0, 1, 2, 3, 4],
            "start_time_hours": 9.0, "end_time_hours": 18.0,
            "lunch_duration_hours": 1.0, "is_default": False
        }

        result = repo.create_schedule(
            name="New Schedule",
            work_days=[0, 1, 2, 3, 4],
            start_time_hours=9.0,
            end_time_hours=18.0,
            lunch_duration_hours=1.0,
            is_default=False,
        )

        assert result is not None
        assert result.name == "New Schedule"

    def test_create_schedule_sets_default(self, repo, mock_db):
        """Test creating a default schedule unsets other defaults."""
        mock_db.fetch_one.return_value = {
            "id": 1, "name": "New Default", "work_days": [0, 1, 2, 3, 4],
            "start_time_hours": 8.5, "end_time_hours": 17.5,
            "lunch_duration_hours": 1.0, "is_default": True
        }

        result = repo.create_schedule(
            name="New Default",
            work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5,
            end_time_hours=17.5,
            lunch_duration_hours=1.0,
            is_default=True,
        )

        # Should have called execute to unset other defaults
        assert mock_db.execute.called

    def test_update_schedule(self, repo, mock_db):
        """Test updating a schedule."""
        mock_db.fetch_one.side_effect = [
            {  # get_schedule_by_id
                "id": 1, "name": "Old Name", "work_days": [0, 1, 2, 3, 4],
                "start_time_hours": 8.5, "end_time_hours": 17.5,
                "lunch_duration_hours": 1.0, "is_default": False
            },
            {  # update query
                "id": 1, "name": "New Name", "work_days": [0, 1, 2, 3, 4],
                "start_time_hours": 8.5, "end_time_hours": 17.5,
                "lunch_duration_hours": 1.0, "is_default": False
            }
        ]

        result = repo.update_schedule(1, name="New Name")

        assert result is not None
        assert result.name == "New Name"

    def test_update_schedule_sets_default(self, repo, mock_db):
        """Test updating schedule to default unsets other defaults."""
        mock_db.fetch_one.side_effect = [
            {  # get_schedule_by_id
                "id": 1, "name": "Old Name", "work_days": [0, 1, 2, 3, 4],
                "start_time_hours": 8.5, "end_time_hours": 17.5,
                "lunch_duration_hours": 1.0, "is_default": False
            },
            {  # update query
                "id": 1, "name": "New Name", "work_days": [0, 1, 2, 3, 4],
                "start_time_hours": 8.5, "end_time_hours": 17.5,
                "lunch_duration_hours": 1.0, "is_default": True
            }
        ]

        result = repo.update_schedule(1, is_default=True)

        # Should have called execute to unset other defaults
        assert mock_db.execute.called

    def test_count_work_days(self, repo):
        """Test counting work days between dates."""
        from models.work_schedule import WorkSchedule

        schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )

        start = date(2026, 1, 5)  # Monday
        end = date(2026, 1, 9)    # Friday

        result = repo.count_work_days(start, end, schedule)

        assert result == 5  # 5 work days (Mon-Fri)

    def test_count_work_days_negative(self, repo):
        """Test counting work days with reversed dates."""
        from models.work_schedule import WorkSchedule

        schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )

        start = date(2026, 1, 9)  # Friday
        end = date(2026, 1, 5)    # Monday

        result = repo.count_work_days(start, end, schedule)

        assert result == -5  # Negative because end < start

    def test_add_work_days(self, repo):
        """Test adding work days to a date."""
        from models.work_schedule import WorkSchedule

        schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )

        start = date(2026, 1, 5)  # Monday

        result = repo.add_work_days(start, 5, schedule)

        assert result == date(2026, 1, 12)  # Next Monday (5 work days, skipping weekend)

    def test_add_work_days_skips_weekend(self, repo):
        """Test that add_work_days skips weekends."""
        from models.work_schedule import WorkSchedule

        schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )

        start = date(2026, 1, 3)  # Saturday

        result = repo.add_work_days(start, 1, schedule)

        assert result == date(2026, 1, 5)  # Monday (next work day)

    def test_add_work_days_zero(self, repo):
        """Test adding zero work days returns same date."""
        from models.work_schedule import WorkSchedule

        schedule = WorkSchedule(
            id=0, name="default", work_days=[0, 1, 2, 3, 4],
            start_time_hours=8.5, end_time_hours=17.5, lunch_duration_hours=1.0
        )

        start = date(2026, 1, 5)

        result = repo.add_work_days(start, 0, schedule)

        assert result == start
