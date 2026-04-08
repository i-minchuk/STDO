from datetime import date, timedelta, datetime
from typing import Dict, List, Tuple

from models.user import User
from repositories.time_log_repository import TimeLogRepository


class HeatmapService:
    """Service for generating activity heatmaps for employees."""

    def __init__(self, time_log_repo: TimeLogRepository) -> None:
        self._time_log_repo = time_log_repo

    def generate_weekly_heatmap(
        self, user_id: int, weeks: int = 12
    ) -> Dict[str, Dict[str, float]]:
        """Generate a weekly heatmap of work hours for a user.

        Returns:
            Dict where key is week (YYYY-WW), value is dict with days (Mon-Sun) and hours.
        """
        today = date.today()
        start_date = today - timedelta(weeks=weeks)
        
        logs = self._time_log_repo.get_by_user_id(user_id, start_date, today)
        
        heatmap: Dict[str, Dict[str, float]] = {}
        
        for log in logs:
            week_key = f"{log.day.year}-W{log.day.isocalendar()[1]:02d}"
            day_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][log.day.weekday()]
            
            if week_key not in heatmap:
                heatmap[week_key] = {day: 0.0 for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
            
            heatmap[week_key][day_name] += log.hours
        
        return heatmap

    def generate_monthly_heatmap(
        self, user_id: int, months: int = 12
    ) -> Dict[str, float]:
        """Generate a monthly heatmap of work hours for a user.

        Returns:
            Dict where key is month (YYYY-MM), value is total hours.
        """
        today = date.today()
        start_date = today.replace(year=today.year - (months // 12), month=today.month - (months % 12))
        start_date = start_date.replace(day=1)
        
        logs = self._time_log_repo.get_by_user_id(user_id, start_date, today)
        
        heatmap: Dict[str, float] = {}
        
        for log in logs:
            month_key = f"{log.day.year}-{log.day.month:02d}"
            heatmap[month_key] = heatmap.get(month_key, 0.0) + log.hours
        
        return heatmap

    def get_user_activity_summary(
        self, user_id: int, days: int = 30
    ) -> Dict[str, float]:
        """Get summary of user activity over the last N days."""
        today = date.today()
        start_date = today - timedelta(days=days)
        
        logs = self._time_log_repo.get_by_user_id(user_id, start_date, today)
        
        total_hours = sum(log.hours for log in logs)
        work_days = sum(1 for log in logs if log.day.weekday() < 5)  # Mon-Fri
        
        avg_daily_hours = total_hours / work_days if work_days > 0 else 0.0
        
        return {
            "total_hours": round(total_hours, 2),
            "work_days": work_days,
            "avg_daily_hours": round(avg_daily_hours, 2),
            "total_entries": len(logs),
        }