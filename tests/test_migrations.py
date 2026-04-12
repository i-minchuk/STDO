"""Integration tests for Alembic migrations.

Tests that migrations can be applied to a fresh database.

Usage:
    pytest tests/test_migrations.py -v
"""

import pytest
import subprocess
import os
from typing import Generator


@pytest.fixture(scope="module")
def fresh_database() -> Generator[str, None, None]:
    """Create a fresh test database."""
    db_name = "iris_migration_test"
    
    # Create database
    print(f"\nCreating fresh database: {db_name}")
    subprocess.run(
        ["createdb", db_name],
        capture_output=True,
        check=False
    )
    
    yield db_name
    
    # Drop database after tests
    print(f"\nDropping database: {db_name}")
    subprocess.run(
        ["dropdb", db_name],
        capture_output=True,
        check=False
    )


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("RUN_MIGRATION_TESTS"),
    reason="Set RUN_MIGRATION_TESTS=1 to run migration tests"
)
def test_alembic_upgrade_head(fresh_database: str):
    """Test that Alembic can upgrade to head on fresh database."""
    dsn = f"postgresql://test:test@localhost/{fresh_database}"
    
    result = subprocess.run(
        ["alembic", "upgrade", "head", "--database", dsn],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Migration failed: {result.stderr}"
    assert "Applied 4 migrations" in result.stdout or "head" in result.stdout


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("RUN_MIGRATION_TESTS"),
    reason="Set RUN_MIGRATION_TESTS=1 to run migration tests"
)
def test_indexes_created(fresh_database: str):
    """Test that performance indexes were created."""
    dsn = f"postgresql://test:test@localhost/{fresh_database}"
    
    # Upgrade first
    subprocess.run(
        ["alembic", "upgrade", "head", "--database", dsn],
        capture_output=True,
        check=True
    )
    
    # Check for key indexes
    indexes_to_check = [
        "idx_documents_project_id",
        "idx_tasks_project_id",
        "idx_notifications_user_unread",
        "idx_gamification_events_user_date",
    ]
    
    for index in indexes_to_check:
        result = subprocess.run(
            ["psql", dsn, "-c", f"SELECT indexname FROM pg_indexes WHERE indexname = '{index}'"],
            capture_output=True,
            text=True
        )
        assert index in result.stdout, f"Index {index} not found"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("RUN_MIGRATION_TESTS"),
    reason="Set RUN_MIGRATION_TESTS=1 to run migration tests"
)
def test_downgrade_and_upgrade(fresh_database: str):
    """Test that downgrade and upgrade work correctly."""
    dsn = f"postgresql://test:test@localhost/{fresh_database}"
    
    # Upgrade
    result = subprocess.run(
        ["alembic", "upgrade", "head", "--database", dsn],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    
    # Downgrade one step
    result = subprocess.run(
        ["alembic", "downgrade", "-1", "--database", dsn],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    
    # Upgrade back
    result = subprocess.run(
        ["alembic", "upgrade", "head", "--database", dsn],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


@pytest.mark.integration
def test_database_connection():
    """Test that we can connect to the test database."""
    from db.database import Database
    from config import Config
    
    cfg = Config()
    db = Database(dsn=cfg.db_dsn, min_size=1, max_size=1)
    db.connect()
    
    try:
        row = db.fetch_one("SELECT 1 AS test")
        assert row["test"] == 1
    finally:
        db.close()
