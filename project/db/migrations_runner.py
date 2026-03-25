import os
import psycopg
from psycopg.rows import dict_row

from config import load_config


def run_migrations():
    cfg = load_config()
    conn = psycopg.connect(cfg.db_dsn, row_factory=dict_row)
    conn.autocommit = True

    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    files = sorted(f for f in os.listdir(migrations_dir) if f.endswith(".sql"))

    with conn.cursor() as cur:
        for fname in files:
            path = os.path.join(migrations_dir, fname)
            print(f"Applying migration: {fname}")
            with open(path, "r", encoding="utf-8") as f:
                sql = f.read()
            cur.execute(sql)

    conn.close()


if __name__ == "__main__":
    run_migrations()