from datetime import date, datetime, timedelta
from repositories.work_schedule_repository import WorkScheduleRepository
from models.work_schedule import WorkSchedule


class TimeCalculationService:
    """Service for calculating deadlines and durations respecting work schedules."""

    def __init__(self, work_schedule_repo: WorkScheduleRepository) -> None:
        self._work_schedule_repo = work_schedule_repo

    def calculate_work_days_from_hours(self, work_hours: float) -> int:
        """Calculate number of work days from work hours."""
        schedule = self._work_schedule_repo.get_default_schedule()
        if not schedule:
            # Fallback: 8 hours per day
            return max(1, int(work_hours / 8))
        
        work_hours_per_day = schedule.work_hours_per_day
        return max(1, int(work_hours / work_hours_per_day))

    def calculate_hours_from_work_days(self, work_days: int) -> float:
        """Calculate work hours from number of work days."""
        schedule = self._work_schedule_repo.get_default_schedule()
        if not schedule:
            return work_days * 8  # Fallback: 8 hours per day
        
        return work_days * schedule.work_hours_per_day

    def add_work_days_to_date(self, start_date: date, days: int) -> date:
        """Add work days to a date, skipping weekends."""
        schedule = self._work_schedule_repo.get_default_schedule()
        if not schedule:
            # Fallback: assume Mon-Fri schedule
            schedule = WorkSchedule(0, "default", [0, 1, 2, 3, 4], 8.5, 17.5, 1.0)
        
        return self._work_schedule_repo.add_work_days(start_date, days, schedule)

    def count_work_days_between(self, start_date: date, end_date: date) -> int:
        """Count work days between two dates."""
        schedule = self._work_schedule_repo.get_default_schedule()
        if not schedule:
            schedule = WorkSchedule(0, "default", [0, 1, 2, 3, 4], 8.5, 17.5, 1.0)
        
        return self._work_schedule_repo.count_work_days(start_date, end_date, schedule)

    def calculate_end_date(self, start_date: date, work_days: int) -> date:
        """Calculate end date given start date and work days duration."""
        return self.add_work_days_to_date(start_date, work_days)

    def is_work_day(self, check_date: date) -> bool:
        """Check if a date is a work day."""
        schedule = self._work_schedule_repo.get_default_schedule()
        if not schedule:
            schedule = WorkSchedule(0, "default", [0, 1, 2, 3, 4], 8.5, 17.5, 1.0)
        
        return schedule.is_work_day(check_date.weekday())
