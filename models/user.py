from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    full_name: str
    role: str  # admin | manager | engineer | norm_controller
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @staticmethod
    def from_row(row: dict) -> User:
        """Create User from database row dict (psycopg dict_row)."""
        return User(
            id=int(row["id"]),
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            full_name=row["full_name"],
            role=row["role"],
            is_active=bool(row["is_active"]),
            created_at=row.get("created_at") or row.get("created_at") or None,
            updated_at=row.get("updated_at") or row.get("updated_at") or None,
        )
