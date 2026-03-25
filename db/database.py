import logging
from typing import Any

import psycopg
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)


class Database:
    """Synchronous PostgreSQL wrapper using psycopg 3."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._conn: psycopg.Connection | None = None

    def connect(self) -> None:
        if self._conn is None or self._conn.closed:
            logger.info("Connecting to database")
            self._conn = psycopg.connect(self._dsn, row_factory=dict_row)
            self._conn.autocommit = False

    def close(self) -> None:
        if self._conn is not None and not self._conn.closed:
            self._conn.close()
            self._conn = None
            logger.info("Database connection closed")

    @property
    def connection(self) -> psycopg.Connection:
        if self._conn is None or self._conn.closed:
            raise RuntimeError("Database is not connected. Call connect() first.")
        return self._conn

    def transaction(self):
        return self.connection.transaction()

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict | None:
        with self.connection.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict]:
        with self.connection.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        with self.connection.cursor() as cur:
            cur.execute(query, params)
