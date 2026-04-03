"""
Integration tests with real database.
Tests API endpoints, services, and repositories against actual database.
"""
import pytest
from datetime import date, timedelta

from models.enums import ProjectStatus, DocumentStatus, TaskStatus, TaskType


@pytest.mark.integration
class TestProjectRepository:
    """Integration tests for ProjectRepository with real DB."""

    def test_create_and_retrieve_project(self, test_locator, cleanup_test_db, test_user):
        """Test creating and retrieving a project."""
        project = test_locator.project_repo.insert(
            code="PROJ-INT-001",
            name="Integration Test Project",
            customer="Test Org",
            status=ProjectStatus.ACTIVE,
            manager_id=test_user.id,
            start_date=date.today(),
            end_date_planned=date.today() + timedelta(days=30),
        )

        retrieved = test_locator.project_repo.get_by_id(project.id)
        assert retrieved is not None
        assert retrieved.code == "PROJ-INT-001"
        assert retrieved.name == "Integration Test Project"
        assert retrieved.status == ProjectStatus.ACTIVE

    def test_list_all_projects(self, test_locator, cleanup_test_db, test_user):
        """Test listing all projects."""
        # Create 3 projects
        for i in range(3):
            test_locator.project_repo.insert(
                code=f"PROJ-{i}",
                name=f"Project {i}",
                customer="Test",
                status=ProjectStatus.ACTIVE,
                manager_id=test_user.id,
                start_date=date.today(),
                end_date_planned=date.today(),
            )

        projects = test_locator.project_repo.list_all()
        assert len(projects) == 3

    def test_update_project_status(self, test_locator, cleanup_test_db, test_project):
        """Test updating project status."""
        test_locator.project_repo.update_status(
            test_project.id, ProjectStatus.COMPLETED
        )

        updated = test_locator.project_repo.get_by_id(test_project.id)
        assert updated.status == ProjectStatus.COMPLETED


@pytest.mark.integration
class TestDocumentRepository:
    """Integration tests for DocumentRepository with real DB."""

    def test_create_and_retrieve_document(
        self, test_locator, cleanup_test_db, test_project, test_user
    ):
        """Test creating and retrieving a document."""
        doc = test_locator.document_repo.insert(
            project_id=test_project.id,
            code="DOC-INT-001",
            title="Integration Test Doc",
            discipline="Engineering",
            status=DocumentStatus.IN_WORK,
            created_by=test_user.id,
        )

        retrieved = test_locator.document_repo.get_by_id(doc.id)
        assert retrieved is not None
        assert retrieved.code == "DOC-INT-001"
        assert retrieved.status == DocumentStatus.IN_WORK

    def test_get_documents_by_project(
        self, test_locator, cleanup_test_db, test_project, test_user
    ):
        """Test retrieving documents by project."""
        for i in range(2):
            test_locator.document_repo.insert(
                project_id=test_project.id,
                code=f"DOC-{i}",
                title=f"Doc {i}",
                discipline="Engineering",
                status=DocumentStatus.IN_WORK,
                created_by=test_user.id,
            )

        docs = test_locator.document_repo.get_by_project_id(test_project.id)
        assert len(docs) == 2


@pytest.mark.integration
class TestRevisionService:
    """Integration tests for RevisionService with real DB."""

    def test_create_revision_full_workflow(
        self, test_locator, cleanup_test_db, test_document, test_user
    ):
        """Test creating revision through full workflow."""
        from io import BytesIO

        file_content = BytesIO(b"Revision content")

        revision = test_locator.revision_service.create_revision(
            document_id=test_document.id,
            filename="test.txt",
            file_content=file_content,
            change_log="First revision",
            created_by=test_user.id,
            major=False,
        )

        assert revision is not None
        assert revision.revision_index == "A01"
        assert revision.revision_letter == "A"
        assert revision.revision_number == 1

    def test_create_major_revision(
        self, test_locator, cleanup_test_db, test_document, test_user
    ):
        """Test creating major revision increments letter."""
        from io import BytesIO

        # Create first revision
        file_content = BytesIO(b"Content 1")
        rev1 = test_locator.revision_service.create_revision(
            document_id=test_document.id,
            filename="v1.txt",
            file_content=file_content,
            change_log="v1",
            created_by=test_user.id,
            major=False,
        )

        # Create major revision (should increment letter)
        file_content = BytesIO(b"Content 2")
        rev2 = test_locator.revision_service.create_revision(
            document_id=test_document.id,
            filename="v2.txt",
            file_content=file_content,
            change_log="v2",
            created_by=test_user.id,
            major=True,
        )

        assert rev2.revision_letter == "B"
        assert rev2.revision_number == 1


@pytest.mark.integration
class TestPlannedTaskRepository:
    """Integration tests for PlannedTaskRepository with real DB."""

    def test_create_and_retrieve_task(
        self, test_locator, cleanup_test_db, test_project, test_user
    ):
        """Test creating and retrieving a task."""
        task = test_locator.planned_task_repo.insert(
            project_id=test_project.id,
            project_code=test_project.code,
            project_name=test_project.name,
            document_id=None,
            document_code=None,
            revision_id=None,
            revision_index=None,
            name="Integration Test Task",
            task_type=TaskType.ENGINEERING,
            assigned_to=test_user.id,
            owner_name="Test User",
            duration_days_planned=5,
            work_hours_planned=40.0,
            start_date_planned=date.today(),
            end_date_planned=date.today() + timedelta(days=5),
            status=TaskStatus.NOT_STARTED,
        )

        retrieved = test_locator.planned_task_repo.get_by_id(task.id)
        assert retrieved is not None
        assert retrieved.name == "Integration Test Task"
        assert retrieved.status == TaskStatus.NOT_STARTED

    def test_update_task_progress(
        self, test_locator, cleanup_test_db, test_task
    ):
        """Test updating task progress."""
        test_locator.planned_task_repo.update_progress(
            task_id=test_task.id,
            percent_complete=50,
            start_date_actual=date.today(),
            end_date_actual=None,
            actual_hours=20.0,
            status=TaskStatus.IN_PROGRESS,
        )

        updated = test_locator.planned_task_repo.get_by_id(test_task.id)
        assert updated.percent_complete == 50
        assert updated.status == TaskStatus.IN_PROGRESS
        assert updated.actual_hours == 20.0


@pytest.mark.integration
class TestCPMScheduler:
    """Integration tests for CPM scheduler service."""

    def test_cpm_calculation_single_task(
        self, test_locator, cleanup_test_db, test_project, test_task
    ):
        """Test CPM calculation with single task."""
        critical_ids = test_locator.cpm_scheduler.recalculate_project_schedule(
            test_project.id
        )

        # Single task should be critical
        assert len(critical_ids) == 1
        assert critical_ids[0] == test_task.id

    def test_cpm_calculation_with_dependencies(
        self, test_locator, cleanup_test_db, test_project, test_user
    ):
        """Test CPM calculation with task dependencies."""
        # Create 2 tasks
        task1 = test_locator.planned_task_repo.insert(
            project_id=test_project.id,
            project_code=test_project.code,
            project_name=test_project.name,
            document_id=None,
            document_code=None,
            revision_id=None,
            revision_index=None,
            name="Task 1",
            task_type=TaskType.ENGINEERING,
            assigned_to=test_user.id,
            owner_name="User",
            duration_days_planned=3,
            work_hours_planned=24.0,
            start_date_planned=date.today(),
            end_date_planned=date.today() + timedelta(days=3),
            status=TaskStatus.NOT_STARTED,
        )

        task2 = test_locator.planned_task_repo.insert(
            project_id=test_project.id,
            project_code=test_project.code,
            project_name=test_project.name,
            document_id=None,
            document_code=None,
            revision_id=None,
            revision_index=None,
            name="Task 2",
            task_type=TaskType.REVIEW,
            assigned_to=test_user.id,
            owner_name="User",
            duration_days_planned=2,
            work_hours_planned=16.0,
            start_date_planned=date.today() + timedelta(days=3),
            end_date_planned=date.today() + timedelta(days=5),
            status=TaskStatus.NOT_STARTED,
        )

        # Create dependency: task1 -> task2
        test_locator.dep_repo.insert(
            project_id=test_project.id,
            predecessor_task_id=task1.id,
            successor_task_id=task2.id,
            lag_days=0,
        )

        # Run CPM
        critical_ids = test_locator.cpm_scheduler.recalculate_project_schedule(
            test_project.id
        )

        # Both tasks should be critical (in series)
        assert len(critical_ids) >= 1

        # Verify ES/EF/LS/LF were calculated
        updated_task1 = test_locator.planned_task_repo.get_by_id(task1.id)
        assert updated_task1.es is not None
        assert updated_task1.ef is not None
        assert updated_task1.ls is not None
        assert updated_task1.lf is not None
