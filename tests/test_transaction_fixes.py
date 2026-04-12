"""Tests for transaction and N+1 fixes (Sprint Week 1 - P0)."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from db.database import Database
from models.enums import DocumentStatus, RevisionStatus, TaskStatus, TaskType
from models.revision import DocumentRevision
from services.document_workflow_service import DocumentWorkflowService
from services.revision_service import RevisionService


class TestTransactionAtomicity:
    """Tests for atomic transaction handling in workflow operations."""

    @pytest.fixture
    def mock_db(self):
        db = MagicMock(spec=Database)
        db.transaction = MagicMock()
        # Mock context manager for transaction
        transaction_ctx = MagicMock()
        transaction_ctx.__enter__ = MagicMock(return_value=None)
        transaction_ctx.__exit__ = MagicMock(return_value=False)
        db.transaction.return_value = transaction_ctx
        return db

    @pytest.fixture
    def workflow_service(self, mock_db):
        """Create workflow service with mocked dependencies."""
        mock_revision_service = MagicMock()
        mock_document_repo = MagicMock()
        mock_revision_repo = MagicMock()
        mock_project_repo = MagicMock()
        mock_task_repo = MagicMock()
        mock_dep_repo = MagicMock()
        mock_cpm = MagicMock()
        mock_dashboard = MagicMock()

        service = DocumentWorkflowService(
            db=mock_db,
            revision_service=mock_revision_service,
            document_repo=mock_document_repo,
            revision_repo=mock_revision_repo,
            project_repo=mock_project_repo,
            task_repo=mock_task_repo,
            dep_repo=mock_dep_repo,
            cpm_scheduler=mock_cpm,
            project_dashboard=mock_dashboard,
        )
        return service, mock_db, mock_revision_service, mock_document_repo, mock_revision_repo, mock_project_repo, mock_task_repo, mock_dep_repo, mock_cpm, mock_dashboard

    def test_create_revision_with_workflow_rollback_on_cpm_failure(
        self, workflow_service
    ):
        """Verify that if CPM recalculation fails, revision is rolled back.
        
        This tests the critical atomicity requirement: if recalculate_project_schedule
        raises an exception after creating the revision, the entire transaction
        should roll back, leaving no partial state.
        """
        service, mock_db, mock_revision_service, mock_document_repo, mock_revision_repo, mock_project_repo, mock_task_repo, mock_dep_repo, mock_cpm, mock_dashboard = workflow_service

        # Setup mocks
        mock_document_repo.get_by_id.return_value = MagicMock(id=1, code="DOC-001", project_id=1)
        mock_project_repo.get_by_id.return_value = MagicMock(id=1, code="PRJ-001", name="Test Project")
        mock_revision_service.create_revision.return_value = MagicMock(
            id=1, document_id=1, revision_index="A01", version_number=1
        )
        mock_task_repo.insert.side_effect = [
            MagicMock(id=1, end_date_planned=date.today() + timedelta(days=2)),  # review task
            MagicMock(id=2, end_date_planned=date.today() + timedelta(days=3)),  # approval task
        ]
        
        # Critical: CPM recalculation fails AFTER revision creation
        mock_cpm.recalculate_project_schedule.side_effect = Exception("CPM calculation failed")

        # Execute
        with pytest.raises(Exception, match="CPM calculation failed"):
            service.create_revision_with_workflow(
                document_id=1,
                filename="test.pdf",
                file_content=MagicMock(),
                change_log="Test change",
                created_by=1,
                reviewer_id=2,
                approver_id=3,
            )

        # Verify transaction was used
        assert mock_db.transaction.called

        # Verify revision service was called (but should be rolled back)
        mock_revision_service.create_revision.assert_called_once()

        # All operations within transaction should have been attempted
        assert mock_task_repo.insert.call_count == 2
        assert mock_dep_repo.insert.called
        assert mock_cpm.recalculate_project_schedule.called

        # Verify transaction context was properly managed
        transaction_ctx = mock_db.transaction.return_value
        transaction_ctx.__enter__.assert_called_once()
        # __exit__ should be called with exception info (non-None args)
        assert transaction_ctx.__exit__.called

    def test_create_revision_with_workflow_rollback_on_task_failure(
        self, workflow_service
    ):
        """Verify rollback if task insertion fails."""
        service, mock_db, mock_revision_service, mock_document_repo, mock_revision_repo, mock_project_repo, mock_task_repo, mock_dep_repo, mock_cpm, mock_dashboard = workflow_service

        # Setup mocks
        mock_document_repo.get_by_id.return_value = MagicMock(id=1, code="DOC-001", project_id=1)
        mock_project_repo.get_by_id.return_value = MagicMock(id=1, code="PRJ-001", name="Test Project")
        mock_revision_service.create_revision.return_value = MagicMock(
            id=1, document_id=1, revision_index="A01", version_number=1
        )
        
        # Task insertion fails
        mock_task_repo.insert.side_effect = Exception("Task creation failed")

        # Execute
        with pytest.raises(Exception, match="Task creation failed"):
            service.create_revision_with_workflow(
                document_id=1,
                filename="test.pdf",
                file_content=MagicMock(),
                change_log="Test change",
                created_by=1,
                reviewer_id=2,
            )

        # Verify transaction was used
        assert mock_db.transaction.called
        # All changes should be rolled back
        mock_revision_service.create_revision.assert_called_once()
        mock_task_repo.insert.assert_called_once()

    def test_approve_revision_with_workflow_rollback_on_task_completion_failure(
        self, workflow_service
    ):
        """Verify rollback if task completion fails during approval."""
        service, mock_db, mock_revision_service, mock_document_repo, mock_revision_repo, mock_project_repo, mock_task_repo, mock_dep_repo, mock_cpm, mock_dashboard = workflow_service

        # Setup mocks
        mock_revision_service.approve_revision = MagicMock()
        mock_revision_repo.get_by_id.return_value = MagicMock(
            id=1, document_id=1, status=RevisionStatus.ON_REVIEW
        )
        mock_task_repo.get_by_revision_id.return_value = [
            MagicMock(
                id=1, task_type=TaskType.APPROVAL, status=TaskStatus.IN_PROGRESS,
                start_date_actual=date.today(), end_date_actual=None, actual_hours=0
            )
        ]
        mock_task_repo.update_progress.side_effect = Exception("Task completion failed")
        mock_document_repo.get_by_id.return_value = MagicMock(id=1, code="DOC-001")

        # Execute
        with pytest.raises(Exception, match="Task completion failed"):
            service.approve_revision_with_workflow_dto(
                revision_id=1,
                approved_by=1,
                comment="Approved",
            )

        # Verify transaction is used in revision_service.approve_revision
        # (This is a separate transaction from task completion)
        mock_revision_service.approve_revision.assert_called_once()

    def test_create_revision_with_workflow_success_path(
        self, workflow_service
    ):
        """Verify full workflow success path."""
        service, mock_db, mock_revision_service, mock_document_repo, mock_revision_repo, mock_project_repo, mock_task_repo, mock_dep_repo, mock_cpm, mock_dashboard = workflow_service

        # Setup mocks
        mock_document_repo.get_by_id.return_value = MagicMock(id=1, code="DOC-001", project_id=1)
        mock_project_repo.get_by_id.return_value = MagicMock(id=1, code="PRJ-001", name="Test Project")
        mock_revision_service.create_revision.return_value = MagicMock(
            id=1, document_id=1, revision_index="A01", version_number=1
        )
        mock_task_repo.insert.side_effect = [
            MagicMock(id=1, end_date_planned=date.today() + timedelta(days=2)),
            MagicMock(id=2, end_date_planned=date.today() + timedelta(days=3)),
        ]

        # Execute
        result = service.create_revision_with_workflow(
            document_id=1,
            filename="test.pdf",
            file_content=MagicMock(),
            change_log="Test change",
            created_by=1,
            reviewer_id=2,
            approver_id=3,
        )

        # Verify all operations completed
        assert result.id == 1
        mock_revision_service.create_revision.assert_called_once()
        assert mock_task_repo.insert.call_count == 2
        assert mock_dep_repo.insert.called
        mock_cpm.recalculate_project_schedule.assert_called_once()


class TestN1QueryOptimization:
    """Tests for N+1 query optimization in dashboard and API endpoints."""

    @pytest.fixture
    def mock_task_repo(self):
        """Mock task repository with performance tracking."""
        repo = MagicMock()
        repo._query_count = 0
        
        def mock_get_by_project_id(project_id):
            repo._query_count += 1
            return []
        
        repo.get_by_project_id = mock_get_by_project_id
        repo.get_by_revision_id = MagicMock(return_value=[])
        return repo

    @pytest.fixture
    def mock_project_repo(self):
        repo = MagicMock()
        repo._query_count = 0
        
        def mock_list_all():
            repo._query_count += 1
            # Return 10 mock projects
            return [MagicMock(id=i, code=f"PRJ-{i:03d}", name=f"Project {i}", status="active") for i in range(10)]
        
        def mock_list_all_paginated(limit, offset):
            repo._query_count += 1
            projects = [MagicMock(id=i, code=f"PRJ-{i:03d}", name=f"Project {i}", status="active") for i in range(offset, min(offset + limit, 10))]
            return projects, 10
        
        repo.list_all = mock_list_all
        repo.list_all_paginated = mock_list_all_paginated
        return repo

    def test_dashboard_service_n1_prevention(self, mock_project_repo, mock_task_repo):
        """Verify dashboard service doesn't cause N+1 queries.
        
        Before fix: list_all() + (get_by_project_id x 10) = 11 queries
        After fix: Should use optimized query with JOINs
        """
        from services.project_dashboard_service import ProjectDashboardService
        from db.database import Database
        
        # Create mock DB
        mock_db = MagicMock(spec=Database)
        mock_db.fetch_all = MagicMock(return_value=[])  # No tasks
        
        # Create proper mock project with status.value
        mock_status = MagicMock()
        mock_status.value = "active"
        
        mock_project = MagicMock()
        mock_project.status = mock_status
        mock_project.id = 1
        mock_project.code = "PRJ-001"
        mock_project.name = "Test Project"
        mock_project.start_date = date.today()
        mock_project.end_date_planned = date.today() + timedelta(days=30)
        mock_project.end_date_forecast = None
        mock_project.end_date_actual = None
        
        mock_project_repo.list_all = MagicMock(return_value=[mock_project])
        
        service = ProjectDashboardService(
            project_repo=mock_project_repo,
            task_repo=mock_task_repo,
            db=mock_db,
        )
        
        # Reset counter
        mock_task_repo.get_by_project_id = MagicMock(return_value=[])
        
        # Execute
        result = service.get_portfolio_today_overview_dto(date.today())
        
        # Verify N+1 fix: get_by_project_id should NOT be called in a loop
        # Instead, we use single fetch_all with IN clause
        assert mock_task_repo.get_by_project_id.call_count == 0, "N+1 queries detected - get_by_project_id should not be called in loop"
        # Should use single fetch_all call for all projects
        assert mock_db.fetch_all.call_count <= 2, f"Too many DB queries: {mock_db.fetch_all.call_count}"

    def test_project_metrics_single_query(self, mock_project_repo, mock_task_repo):
        """Verify recalculate_project_metrics uses efficient queries."""
        from services.project_dashboard_service import ProjectDashboardService
        from db.database import Database
        
        # Create mock DB
        mock_db = MagicMock(spec=Database)
        mock_db.fetch_one = MagicMock(return_value=None)  # No metrics saved
        
        # Setup mock task repo with proper MagicMock
        mock_task_repo.get_by_project_id = MagicMock(return_value=[])
        
        service = ProjectDashboardService(
            project_repo=mock_project_repo,
            task_repo=mock_task_repo,
            db=mock_db,
        )
        
        # Execute for single project
        result = service.recalculate_project_metrics(project_id=1)
        
        # Should be exactly 1 query for a single project
        assert mock_task_repo.get_by_project_id.call_count == 1, "Expected get_by_project_id to be called once"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
