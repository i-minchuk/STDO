"""
PyTest configuration and fixtures for integration tests.
"""
import os
import pytest
from datetime import date, datetime, timezone

from db.database import Database
from config import Config
from core.service_locator import ServiceLocator, init_locator, get_locator
from models.enums import ProjectStatus, DocumentStatus, TaskStatus, TaskType


@pytest.fixture(scope="function")
def test_db() -> Database:
    """Create test database connection (single connection, not pool)."""
    db_dsn = os.getenv(
        "TEST_DB_DSN",
        "postgresql://postgres:Qwerty852@localhost:5432/iris_test",
    )
    db = Database(db_dsn, min_size=1, max_size=1)
    db.connect()
    yield db
    db.close()


@pytest.fixture(scope="function")
def test_locator(test_db) -> ServiceLocator:
    """Create service locator with test database."""
    cfg = Config(
        db_dsn="postgresql://postgres:Qwerty852@localhost:5432/iris_test",
        storage_root="/tmp/iris_test_storage",
    )
    locator = ServiceLocator(cfg)
    init_locator(cfg)
    yield locator
    locator.db.close()


@pytest.fixture(scope="function")
def cleanup_test_db(test_db):
    """Clean up test database before each test."""
    # Clean up in dependency order (foreign keys first)
    cleanup_sql = """
    TRUNCATE TABLE gamification_events CASCADE;
    TRUNCATE TABLE time_logs CASCADE;
    TRUNCATE TABLE remarks CASCADE;
    TRUNCATE TABLE vdr_mdr CASCADE;
    TRUNCATE TABLE task_dependencies CASCADE;
    TRUNCATE TABLE planned_tasks CASCADE;
    TRUNCATE TABLE document_revisions CASCADE;
    TRUNCATE TABLE documents CASCADE;
    TRUNCATE TABLE projects CASCADE;
    TRUNCATE TABLE users CASCADE;
    """
    with test_db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(cleanup_sql)
        conn.commit()
    yield
    # Clean up after test
    with test_db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(cleanup_sql)
        conn.commit()


@pytest.fixture
def test_user(test_locator, cleanup_test_db):
    """Create test user."""
    user = test_locator.user_repo.create(
        username="testuser",
        email="test@example.com",
        password_hash=test_locator.auth_service.hash_password("TestPass123"),
        full_name="Test User",
        role="engineer",
    )
    return user


@pytest.fixture
def test_project(test_locator, test_user, cleanup_test_db):
    """Create test project."""
    project = test_locator.project_repo.insert(
        code="PROJ001",
        name="Test Project",
        customer="Test Customer",
        status=ProjectStatus.ACTIVE,
        manager_id=test_user.id,
        start_date=date.today(),
        end_date_planned=date.today(),
    )
    return project


@pytest.fixture
def test_document(test_locator, test_project, test_user, cleanup_test_db):
    """Create test document."""
    doc = test_locator.document_repo.insert(
        project_id=test_project.id,
        code="DOC001",
        title="Test Document",
        discipline="Engineering",
        status=DocumentStatus.IN_WORK,
        created_by=test_user.id,
    )
    return doc


@pytest.fixture
def test_revision(test_locator, test_document, test_user, cleanup_test_db):
    """Create test revision."""
    # Create a temporary file for testing
    import tempfile
    from io import BytesIO

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test revision content")
        f.flush()
        file_path = f.name

    # Create revision using revision repo directly
    revision = test_locator.revision_repo.insert(
        document_id=test_document.id,
        revision_index="A01",
        revision_letter="A",
        revision_number=1,
        version_number=1,
        status="draft",
        file_path=file_path,
        change_log="Initial version",
        created_by=test_user.id,
    )

    # Update document current_revision
    test_locator.document_repo.update_current_revision(
        test_document.id, revision.id
    )

    yield revision

    # Cleanup
    if os.path.exists(file_path):
        os.unlink(file_path)


@pytest.fixture
def test_task(test_locator, test_project, test_user, cleanup_test_db):
    """Create test planned task."""
    task = test_locator.planned_task_repo.insert(
        project_id=test_project.id,
        project_code=test_project.code,
        project_name=test_project.name,
        document_id=None,
        document_code=None,
        revision_id=None,
        revision_index=None,
        name="Test Task",
        task_type=TaskType.ENGINEERING,
        assigned_to=test_user.id,
        owner_name="Test User",
        duration_days_planned=5,
        work_hours_planned=40.0,
        start_date_planned=date.today(),
        end_date_planned=date.today(),
        status=TaskStatus.NOT_STARTED,
    )
    return task
