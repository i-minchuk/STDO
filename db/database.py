import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL wrapper with simple connections (no pooling).
    
    Note: Connection pooling was temporarily removed due to psycopg_pool deadlocks
    in async FastAPI context on Windows. For production, consider:
    1. Using async psycopg with AsyncConnectionPool
    2. Running on Linux where pooling works more reliably
    3. Using PgBouncer as external connection pooler
    """

    def __init__(self, dsn: str, min_size: int = 3, max_size: int = 20) -> None:
        """Initialize database.

        Args:
            dsn: PostgreSQL connection string
            min_size: kept for API compatibility (not used)
            max_size: kept for API compatibility (not used)
        """
        self._dsn = dsn
        # Parameters kept for ServiceLocator compatibility
        _ = min_size, max_size
        logger.info("Database initialized")

    def connect(self) -> None:
        """No-op: connections created on demand in get_connection()."""
        pass

    def close(self) -> None:
        """No-op: connections closed after each use."""
        pass

    @contextmanager
    def get_connection(self) -> Generator[Connection, None, None]:
        """Get a fresh connection."""
        logger.debug("Opening new database connection")
        conn = psycopg.connect(self._dsn, autocommit=False)
        conn.row_factory = dict_row
        try:
            conn.execute("SET TIME ZONE 'UTC'")
            yield conn
        finally:
            try:
                conn.rollback()  # Rollback any uncommitted changes
            except:
                pass
            conn.close()
            logger.debug("Database connection closed")

    @contextmanager
    def transaction(self) -> Generator[Connection, None, None]:
        """Open a transaction."""
        with self.get_connection() as conn:
            with conn.transaction():
                yield conn

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict | None:
        """Fetch one row."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict]:
        """Fetch all rows."""
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

