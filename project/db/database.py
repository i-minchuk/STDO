# db/database.py
from typing import Any, Iterable
import psycopg
from psycopg.rows import dict_row


class Database:
    def __init__(self, dsn: str):
        self._dsn = dsn
        self._conn: psycopg.Connection | None = None

    def connect(self) -> None:
        if self._conn is None:
            self._conn = psycopg.connect(self._dsn, row_factory=dict_row)
            self._conn.autocommit = False

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def transaction(self):
        if self._conn is None:
            raise RuntimeError("Database is not connected")
        return self._conn.transaction()

    def fetch_one(self, query: str, params: Iterable[Any] = ()) -> dict | None:
        with self._conn.cursor() as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return row

    def fetch_all(self, query: str, params: Iterable[Any] = ()) -> list[dict]:
        with self._conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return rows

    def execute(self, query: str, params: Iterable[Any] = ()) -> None:
        with self._conn.cursor() as cur:
            cur.execute(query, params)