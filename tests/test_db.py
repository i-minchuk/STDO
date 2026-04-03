import os
import sys

# Добавляем корень проекта в sys.path
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import Config
import psycopg2

cfg = Config()
print("Используемый DSN:", cfg.db_dsn)

conn = psycopg2.connect(cfg.db_dsn)
cur = conn.cursor()
cur.execute("SELECT 1;")
print("Результат SELECT 1:", cur.fetchone())
conn.close()