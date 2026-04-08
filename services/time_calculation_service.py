import math
from datetime import date

from models.work_schedule import WorkSchedule
from repositories.work_schedule_repository import WorkScheduleRepository


class TimeCalculationService:
    """Service for calculating deadlines and durations respecting work schedules."""

    def __init__(self, work_schedule_repo: WorkScheduleRepository) -> None:
        self._work_schedule_repo = work_schedule_repo

    @staticmethod
    def _fallback_schedule() -> WorkSchedule:
        return WorkSchedule(0, "default", [0, 1, 2, 3, 4], 8.5, 17.5, 1.0)

    def _get_schedule_or_fallback(self) -> WorkSchedule:
        schedule = self._work_schedule_repo.get_default_schedule()
        return schedule if schedule else self._fallback_schedule()

    def calculate_work_days_from_hours(self, work_hours: float) -> int:
        """Calculate number of work days from work hours.

        Any partial work day is rounded up to avoid understating duration.
        """
        if work_hours <= 0:
            return 0

        schedule = self._get_schedule_or_fallback()
        work_hours_per_day = schedule.work_hours_per_day
        return math.ceil(work_hours / work_hours_per_day)

    def calculate_hours_from_work_days(self, work_days: int) -> float:
        """Calculate work hours from number of work days."""
        if work_days <= 0:
            return 0

        schedule = self._get_schedule_or_fallback()
        return work_days * schedule.work_hours_per_day

    def add_work_days_to_date(self, start_date: date, days: int) -> date:
        """Add work days to a date, skipping non-working days.

        The start date is treated as day zero. For example:
        - Monday + 0 work days = Monday
        - Monday + 1 work day = Tuesday
        """
        schedule = self._get_schedule_or_fallback()
        return self._work_schedule_repo.add_work_days(start_date, days, schedule)

    def count_work_days_between(self, start_date: date, end_date: date) -> int:
        """Count work days between two dates inclusively.

        Returns a negative value when end_date is earlier than start_date.
        """
        schedule = self._get_schedule_or_fallback()
        return self._work_schedule_repo.count_work_days(start_date, end_date, schedule)

    def calculate_end_date(self, start_date: date, work_days: int) -> date:
        """Calculate end date given start date and work days duration.

        Duration is interpreted as calendar movement in working days:
        - start_date with 0 work days returns start_date
        - start_date with 1 work day returns the next working day
        """
        return self.add_work_days_to_date(start_date, work_days)

    def is_work_day(self, check_date: date) -> bool:
        """Check if a date is a work day."""
        schedule = self._get_schedule_or_fallback()
        return schedule.is_work_day(check_date.weekday())
