import os
import logging
from alembic.config import Config as AlembicConfig
from alembic import command

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    """Run Alembic migrations.

    Uses Alembic to manage database schema changes.
    The DSN is loaded from the Config class via env.py.
    """
    # Get the path to alembic.ini
    alembic_ini_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "alembic.ini"
    )

    if not os.path.exists(alembic_ini_path):
        logger.error("alembic.ini not found at %s", alembic_ini_path)
        return

    try:
        # Create Alembic config
        alembic_cfg = AlembicConfig(alembic_ini_path)

        # Run migrations to the latest revision
        logger.info("Applying Alembic migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("All migrations applied successfully")
    except Exception as e:
        logger.error("Failed to apply migrations: %s", str(e))
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
