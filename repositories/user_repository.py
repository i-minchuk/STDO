from __future__ import annotations
from typing import Optional, List
from models.user import User


class UserRepository:
    _COLUMNS = "id, username, email, password_hash, full_name, role, is_active, created_at, updated_at"

    def __init__(self, db):
        self._db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        row = self._db.fetch_one(
            f"SELECT {self._COLUMNS} FROM users WHERE id = %s", (user_id,)
        )
        return User.from_row(row) if row else None

    def get_by_username(self, username: str) -> Optional[User]:
        row = self._db.fetch_one(
            f"SELECT {self._COLUMNS} FROM users WHERE username = %s", (username,)
        )
        return User.from_row(row) if row else None

    def get_by_email(self, email: str) -> Optional[User]:
        row = self._db.fetch_one(
            f"SELECT {self._COLUMNS} FROM users WHERE email = %s", (email,)
        )
        return User.from_row(row) if row else None

    def get_all(self, active_only: bool = False) -> List[User]:
        sql = f"SELECT {self._COLUMNS} FROM users"
        if active_only:
            sql += " WHERE is_active = TRUE"
        sql += " ORDER BY id"
        rows = self._db.fetch_all(sql)
        return [User.from_row(r) for r in rows]

    def create(self, username: str, email: str, password_hash: str,
               full_name: str, role: str = "engineer") -> User:
        row = self._db.fetch_one(
            f"""INSERT INTO users (username, email, password_hash, full_name, role)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING {self._COLUMNS}""",
            (username, email, password_hash, full_name, role),
        )
        return User.from_row(row)

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        if not kwargs:
            return self.get_by_id(user_id)
        sets = ", ".join(f"{k} = %s" for k in kwargs)
        vals = list(kwargs.values()) + [user_id]
        row = self._db.fetch_one(
            f"UPDATE users SET {sets}, updated_at = NOW() WHERE id = %s RETURNING {self._COLUMNS}",
            tuple(vals),
        )
        return User.from_row(row) if row else None

    def deactivate(self, user_id: int) -> bool:
        self._db.execute(
            "UPDATE users SET is_active = FALSE, updated_at = NOW() WHERE id = %s",
            (user_id,),
        )
        return True

    def count(self) -> int:
        row = self._db.fetch_one("SELECT COUNT(*) FROM users")
        return row[0] if row else 0
