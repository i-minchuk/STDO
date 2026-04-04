from typing import Sequence, Optional
from datetime import date, datetime

from db.database import Database
from models.daily_quest import DailyQuest


class DailyQuestRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = """
        id, user_id, quest_type, title, description, target_count,
        current_count, reward_points, reward_xp, date, is_completed, completed_at
    """

    def get_user_daily_quests(self, user_id: int, quest_date: date) -> Sequence[DailyQuest]:
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM daily_quests WHERE user_id = %s AND date = %s",
            (user_id, quest_date),
        )
        return [self._row_to_model(r) for r in rows]

    def create_daily_quests_for_user(self, user_id: int, quest_date: date) -> Sequence[DailyQuest]:
        """Create default daily quests for user if they don't exist."""
        existing = self.get_user_daily_quests(user_id, quest_date)
        if existing:
            return existing

        quests_data = [
            {
                "quest_type": "complete_tasks",
                "title": "Завершить задачи",
                "description": "Завершите 3 задачи сегодня",
                "target_count": 3,
                "reward_points": 25,
                "reward_xp": 10,
            },
            {
                "quest_type": "create_documents",
                "title": "Создать документы",
                "description": "Создайте 2 новых документа",
                "target_count": 2,
                "reward_points": 30,
                "reward_xp": 15,
            },
            {
                "quest_type": "review_documents",
                "title": "Проверить документы",
                "description": "Проверьте 2 документа",
                "target_count": 2,
                "reward_points": 20,
                "reward_xp": 8,
            },
        ]

        created_quests = []
        for quest_data in quests_data:
            row = self._db.fetch_one(
                f"""
                INSERT INTO daily_quests
                (user_id, quest_type, title, description, target_count,
                 current_count, reward_points, reward_xp, date)
                VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s)
                RETURNING {self._COLUMNS}
                """,
                (
                    user_id, quest_data["quest_type"], quest_data["title"],
                    quest_data["description"], quest_data["target_count"],
                    quest_data["reward_points"], quest_data["reward_xp"], quest_date,
                ),
            )
            created_quests.append(self._row_to_model(row))

        return created_quests

    def update_quest_progress(self, user_id: int, quest_type: str, quest_date: date, increment: int = 1) -> Optional[DailyQuest]:
        """Update quest progress and check for completion."""
        # First, ensure quests exist for the day
        self.create_daily_quests_for_user(user_id, quest_date)

        # Update progress
        row = self._db.fetch_one(
            f"""
            UPDATE daily_quests
            SET current_count = LEAST(current_count + %s, target_count)
            WHERE user_id = %s AND quest_type = %s AND date = %s AND is_completed = false
            RETURNING {self._COLUMNS}
            """,
            (increment, user_id, quest_type, quest_date),
        )

        if not row:
            return None

        quest = self._row_to_model(row)

        # Check if completed
        if quest.current_count >= quest.target_count and not quest.is_completed:
            self._db.execute(
                "UPDATE daily_quests SET is_completed = true, completed_at = %s WHERE id = %s",
                (datetime.now(), quest.id),
            )
            quest.is_completed = True
            quest.completed_at = datetime.now()

        return quest

    def get_completed_quests_count(self, user_id: int, quest_date: date) -> int:
        row = self._db.fetch_one(
            "SELECT COUNT(*) AS count FROM daily_quests WHERE user_id = %s AND date = %s AND is_completed = true",
            (user_id, quest_date),
        )
        return int(row["count"]) if row else 0

    @staticmethod
    def _row_to_model(row: dict) -> DailyQuest:
        return DailyQuest(
            id=row["id"], user_id=row["user_id"], quest_type=row["quest_type"],
            title=row["title"], description=row["description"],
            target_count=row["target_count"], current_count=row["current_count"],
            reward_points=row["reward_points"], reward_xp=row["reward_xp"],
            date=row["date"], is_completed=row["is_completed"],
            completed_at=row.get("completed_at"),
        )