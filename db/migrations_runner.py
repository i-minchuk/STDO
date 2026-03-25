import os
import logging

import psycopg
from psycopg.rows import dict_row

from config import load_config

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    cfg = load_config()
    conn = psycopg.connect(cfg.db_dsn, row_factory=dict_row)
    conn.autocommit = True

    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    if not os.path.isdir(migrations_dir):
        logger.warning("Migrations directory not found: %s", migrations_dir)
        return

    files = sorted(f for f in os.listdir(migrations_dir) if f.endswith(".sql"))

    with conn.cursor() as cur:
        for fname in files:
            path = os.path.join(migrations_dir, fname)
            sql = open(path, "r", encoding="utf-8").read().strip()
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
