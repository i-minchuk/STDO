from typing import Sequence, Optional
from datetime import datetime, date, timedelta

from db.database import Database
from models.work_schedule import WorkSchedule
from repositories.base_repository import BaseRepository


class WorkScheduleRepository(BaseRepository[WorkSchedule]):
    """Repository for work schedules with BaseRepository for CRUD operations.
    
    Migrated to BaseRepository to reduce boilerplate.
    Custom methods: get_default_schedule, create_schedule, update_schedule,
                    count_work_days, add_work_days, add_work_hours
    """

    def __init__(self, db: Database) -> None:
        super().__init__(
            db=db,
            model_class=WorkSchedule,
            table_name="work_schedules",
            columns="id, name, work_days, start_time_hours, end_time_hours, lunch_duration_hours, is_default"
        )

    def get_default_schedule(self) -> Optional[WorkSchedule]:
        """Get the default work schedule."""
        row = self._db.fetch_one(
            f"SELECT {self._columns} FROM {self._table_name} WHERE is_default = true LIMIT 1"
        )
        return self._row_to_model(row) if row else None

    def get_schedule_by_id(self, schedule_id: int) -> Optional[WorkSchedule]:
        """Get work schedule by ID (uses BaseRepository.get_by_id)."""
        return self.get_by_id(schedule_id)

    def get_all_schedules(self) -> Sequence[WorkSchedule]:
        """Get all work schedules (uses BaseRepository.list_all)."""
        return self.list_all(order_by="is_default DESC")

    def create_schedule(
        self,
        name: str,
        work_days: list,
        start_time_hours: float,
        end_time_hours: float,
        lunch_duration_hours: float,
        is_default: bool = False,
    ) -> WorkSchedule:
        """Create new work schedule."""
        # If this is default, unset other defaults
        if is_default:
            self._db.execute("UPDATE work_schedules SET is_default = false")

        row = self._db.fetch_one(
            f"""INSERT INTO {self._table_name}
               (name, work_days, start_time_hours, end_time_hours, lunch_duration_hours, is_default)
               VALUES (%s, %s, %s, %s, %s, %s)
               RETURNING {self._columns}""",
            (name, work_days, start_time_hours, end_time_hours, lunch_duration_hours, is_default)
        )
        return self._row_to_model(row)

    def update_schedule(
        self,
        schedule_id: int,
        name: Optional[str] = None,
        work_days: Optional[list] = None,
        start_time_hours: Optional[float] = None,
        end_time_hours: Optional[float] = None,
        lunch_duration_hours: Optional[float] = None,
        is_default: Optional[bool] = None,
    ) -> Optional[WorkSchedule]:
        """Update work schedule."""
        schedule = self.get_schedule_by_id(schedule_id)
        if not schedule:
            return None

        # Build update query
        updates = []
        values = []

        if name is not None:
            updates.append("name = %s")
            values.append(name)
        if work_days is not None:
            updates.append("work_days = %s")
            values.append(work_days)
        if start_time_hours is not None:
            updates.append("start_time_hours = %s")
            values.append(start_time_hours)
        if end_time_hours is not None:
            updates.append("end_time_hours = %s")
            values.append(end_time_hours)
        if lunch_duration_hours is not None:
            updates.append("lunch_duration_hours = %s")
            values.append(lunch_duration_hours)

        if is_default:
            self._db.execute("UPDATE work_schedules SET is_default = false")
            updates.append("is_default = %s")
            values.append(True)

        if not updates:
            return schedule

        values.append(schedule_id)
        query = f"UPDATE {self._table_name} SET {', '.join(updates)} WHERE id = %s RETURNING {self._columns}"
        row = self._db.fetch_one(query, values)
        return self._row_to_model(row) if row else None

    def count_work_days(self, start_date: date, end_date: date, schedule: Optional[WorkSchedule] = None) -> int:
        """Count work days between two dates inclusively.

        Returns a negative value when end_date is earlier than start_date.
        """
        if schedule is None:
            schedule = self.get_default_schedule()
        if schedule is None:
            # Fallback: assume 5-day week (Mon-Fri)
            schedule = WorkSchedule(0, "default", [0, 1, 2, 3, 4], 8.5, 17.5, 1.0)

        if start_date == end_date:
            return 1 if schedule.is_work_day(start_date.weekday()) else 0

        sign = 1
        range_start = start_date
        range_end = end_date
        if end_date < start_date:
            sign = -1
            range_start = end_date
            range_end = start_date

        count = 0
        current = range_start
        while current <= range_end:
            if schedule.is_work_day(current.weekday()):
                count += 1
            current += timedelta(days=1)

        return count * sign

    def add_work_days(self, start_date: date, days_count: int, schedule: Optional[WorkSchedule] = None) -> date:
        """Add N work days to a date.

        The start date is treated as day zero.
        """
        if schedule is None:
            schedule = self.get_default_schedule()
        if schedule is None:
            schedule = WorkSchedule(0, "default", [0, 1, 2, 3, 4], 8.5, 17.5, 1.0)

        if days_count == 0:
            return start_date

        current = start_date
        added = 0
        step = 1 if days_count > 0 else -1
        target = abs(days_count)

        while added < target:
            current += timedelta(days=step)
            if schedule.is_work_day(current.weekday()):
                added += 1

        return current

    def add_work_hours(self, start_time: datetime, hours: float, schedule: Optional[WorkSchedule] = None) -> datetime:
        """Add work hours to a datetime, respecting work schedule."""
        if schedule is None:
            schedule = self.get_default_schedule()
        if schedule is None:
            schedule = WorkSchedule(0, "default", [0, 1, 2, 3, 4], 8.5, 17.5, 1.0)

        current = start_time
        remaining_hours = hours

        while remaining_hours > 0:
            # Skip to next work day if current is not a work day
            if not schedule.is_work_day(current.weekday()):
                current = current.replace(hour=int(schedule.start_time_hours), minute=0, second=0)
                if not schedule.is_work_day(current.weekday()):
                    current += timedelta(days=1)
                    continue

            # Calculate hours remaining in current day
            current_hour = current.hour + (current.minute / 60)
            if current_hour < schedule.start_time_hours:
                # Before work start
                current = current.replace(hour=int(schedule.start_time_hours), minute=0, second=0)
                current_hour = schedule.start_time_hours
            elif current_hour >= schedule.end_time_hours:
                # After work end, move to next day
                current += timedelta(days=1)
                current = current.replace(hour=int(schedule.start_time_hours), minute=0, second=0)
                continue

            hours_until_lunch = schedule.start_time_hours + (schedule.work_hours_per_day / 2) - current_hour
            hours_until_end = schedule.end_time_hours - current_hour

            if remaining_hours <= hours_until_lunch:
                # Can finish before lunch
                current += timedelta(hours=remaining_hours)
                remaining_hours = 0
            else:
                # Need to account for lunch break
                current = current.replace(hour=int(schedule.end_time_hours - (schedule.work_hours_per_day / 2)), minute=0, second=0)
                current += timedelta(hours=schedule.lunch_duration_hours)
                remaining_hours -= hours_until_lunch

        return current

    # Note: _row_to_model is inherited from BaseRepository
