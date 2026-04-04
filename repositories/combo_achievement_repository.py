from typing import Sequence, Optional
from datetime import date, datetime, timedelta

from db.database import Database
from models.combo_achievement import ComboAchievement


class ComboAchievementRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = """
        id, user_id, combo_type, current_count, max_count, multiplier, expires_at, is_active
    """

    def get_user_active_combos(self, user_id: int) -> Sequence[ComboAchievement]:
        rows = self._db.fetch_all(
            f"""SELECT {self._COLUMNS}
               FROM combo_achievements
               WHERE user_id = %s AND is_active = true AND expires_at >= %s""",
            (user_id, date.today()),
        )
        return [self._row_to_model(r) for r in rows]

    def get_or_create_combo(self, user_id: int, combo_type: str) -> ComboAchievement:
        """Get active combo or create new one if expired."""
        row = self._db.fetch_one(
            f"""SELECT {self._COLUMNS}
               FROM combo_achievements
               WHERE user_id = %s AND combo_type = %s AND is_active = true AND expires_at >= %s
               ORDER BY expires_at DESC LIMIT 1""",
            (user_id, combo_type, date.today()),
        )

        if row:
            return self._row_to_model(row)

        # Create new combo (5-day window)
        expires_at = date.today() + timedelta(days=5)
        row = self._db.fetch_one(
            f"""INSERT INTO combo_achievements
               (user_id, combo_type, current_count, max_count, multiplier, expires_at, is_active)
               VALUES (%s, %s, 0, 10, 1.0, %s, true)
               RETURNING {self._COLUMNS}""",
            (user_id, combo_type, expires_at),
        )
        return self._row_to_model(row)

    def increment_combo(self, user_id: int, combo_type: str) -> ComboAchievement:
        """Increment combo counter and calculate bonus multiplier."""
        combo = self.get_or_create_combo(user_id, combo_type)

        # Increment counter (capped at max_count)
        new_count = min(combo.current_count + 1, combo.max_count)
        
        # Calculate new multiplier (increases per 3 consecutive actions)
        # 1-3: 1.0x, 4-6: 1.5x, 7-10: 2.0x
        if new_count >= 7:
            multiplier = 2.0
        elif new_count >= 4:
            multiplier = 1.5
        else:
            multiplier = 1.0

        row = self._db.fetch_one(
            f"""UPDATE combo_achievements
               SET current_count = %s, multiplier = %s
               WHERE id = %s
               RETURNING {self._COLUMNS}""",
            (new_count, multiplier, combo.id),
        )
        return self._row_to_model(row)

    def reset_expired_combos(self, user_id: int):
        """Reset expired combos (called periodically)."""
        self._db.execute(
            """UPDATE combo_achievements
               SET is_active = false
               WHERE user_id = %s AND expires_at < %s""",
            (user_id, date.today()),
        )

    def get_combo_multiplier(self, user_id: int, combo_type: str) -> float:
        """Get current combo multiplier for points calculation."""
        combo = self.get_or_create_combo(user_id, combo_type)
        return combo.multiplier

    @staticmethod
    def _row_to_model(row: dict) -> ComboAchievement:
        return ComboAchievement(
            id=row["id"], user_id=row["user_id"], combo_type=row["combo_type"],
            current_count=row["current_count"], max_count=row["max_count"],
            multiplier=row["multiplier"], expires_at=row["expires_at"],
            is_active=row["is_active"],
        )