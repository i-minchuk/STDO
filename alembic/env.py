from logging.config import fileConfig

from alembic import context
import psycopg
from psycopg.errors import Error as PostgresError

# Import Config to get DSN from environment/defaults
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load DSN from Config class - overrides the alembic.ini value
cfg = Config()
config.set_main_option("sqlalchemy.url", cfg.db_dsn)

# add your model's MetaData object here
# for 'autogenerate' support
# For now, models are dataclasses (not SQLAlchemy ORM), so autogenerate is not used
# target_metadata = mymodel.Base.metadata
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create a psycopg connection
    and associate it with the context.

    """
    db_dsn = config.get_main_option("sqlalchemy.url")

    # Use psycopg directly (native PostgreSQL driver)
    conn = psycopg.connect(db_dsn)
    conn.autocommit = True

    try:
        context.configure(
            connection=conn, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
    finally:
        conn.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
