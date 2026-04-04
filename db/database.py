import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL wrapper with connection pooling using psycopg 3."""

    def __init__(self, dsn: str, min_size: int = 2, max_size: int = 10) -> None:
        """Initialize database pool.

        Args:
            dsn: PostgreSQL connection string
            min_size: Minimum pool connections kept open
            max_size: Maximum pool connections
        """
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._pool: Optional[ConnectionPool] = None

    @staticmethod
    def _configure_connection(connection: Connection) -> None:
        """Configure new psycopg connections for the pool."""
        connection.row_factory = dict_row

    def connect(self) -> None:
        """Initialize connection pool."""
        if self._pool is None or self._pool.closed:
            logger.info(
                "Opening database pool: min=%d, max=%d",
                self._min_size,
                self._max_size,
            )
            self._pool = ConnectionPool(
                self._dsn,
                min_size=self._min_size,
                max_size=self._max_size,
                configure=self._configure_connection,
                kwargs={"autocommit": False},
            )

    def close(self) -> None:
        """Close connection pool."""
        if self._pool is not None and not self._pool.closed:
            self._pool.close()
            self._pool = None
            logger.info("Database pool closed")

    @property
    def pool(self) -> ConnectionPool:
        """Get the connection pool."""
        if self._pool is None or self._pool.closed:
            raise RuntimeError("Database pool is not initialized. Call connect() first.")
        return self._pool

    @contextmanager
    def get_connection(self) -> Generator[Connection, None, None]:
        """Get a connection from the pool."""
        with self.pool.connection() as conn:
            yield conn

    @contextmanager
    def transaction(self) -> Generator[Connection, None, None]:
        """Open a transaction on a pooled connection."""
        with self.pool.connection() as conn:
            with conn.transaction():
                yield conn

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict | None:
        """Fetch one row from pool."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict]:
        """Fetch all rows from pool."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        """Execute query without returning results."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
            conn.commit()

