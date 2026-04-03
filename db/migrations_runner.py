import os
import logging

import psycopg
from psycopg.rows import dict_row

from config import Config

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    """Run all SQL migrations from migrations/ directory."""
    cfg = Config()
    # For migrations, use a single connection (not pool)
    conn = psycopg.connect(cfg.db_dsn, row_factory=dict_row)
    conn.autocommit = True

    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    if not os.path.isdir(migrations_dir):
        logger.warning("Migrations directory not found: %s", migrations_dir)
        conn.close()
        return

    files = sorted(f for f in os.listdir(migrations_dir) if f.endswith(".sql"))

    with conn.cursor() as cur:
        for fname in files:
            path = os.path.join(migrations_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                sql = f.read().strip()
            if not sql:
                logger.info("Skipping empty migration: %s", fname)
                continue
            logger.info("Applying migration: %s", fname)
            cur.execute(sql)

    conn.close()
    logger.info("All migrations applied")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
