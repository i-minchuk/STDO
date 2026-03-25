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
    def from_row(row: tuple) -> User:
        return User(
            id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            full_name=row[4],
            role=row[5],
            is_active=bool(row[6]),
            created_at=row[7] if len(row) > 7 else None,
            updated_at=row[8] if len(row) > 8 else None,
        )
