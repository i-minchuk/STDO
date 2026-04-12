import logging
from datetime import date, timedelta
from typing import BinaryIO, Optional

from db.database import Database
from dto.revision import RevisionWorkflowDTO, WorkflowTaskDTO
from models.enums import (
    DocumentStatus,
    RevisionStatus,
    TaskStatus,
    TaskType,
)
from models.revision import DocumentRevision
from repositories.document_repository import DocumentRepository
from repositories.planned_task_repository import PlannedTaskRepository
from repositories.project_repository import ProjectRepository
from repositories.revision_repository import RevisionRepository
from repositories.task_dependency_repository import TaskDependencyRepository
from services.cpm_scheduler_service import CPMSchedulerService
from services.project_dashboard_service import ProjectDashboardService
from services.revision_service import RevisionService

logger = logging.getLogger(__name__)


class DocumentWorkflowService:
    """Orchestrates the full document revision lifecycle: create, review, approve."""

    def __init__(
        self,
        db: Database,
        revision_service: RevisionService,
        document_repo: DocumentRepository,
        revision_repo: RevisionRepository,
        project_repo: ProjectRepository,
        task_repo: PlannedTaskRepository,
        dep_repo: TaskDependencyRepository,
        cpm_scheduler: CPMSchedulerService,
        project_dashboard: ProjectDashboardService,
    ) -> None:
        self._db = db
        self._revision_service = revision_service
        self._documents = document_repo
        self._revisions = revision_repo
        self._projects = project_repo
        self._tasks = task_repo
        self._deps = dep_repo
        self._cpm = cpm_scheduler
        self._dashboard = project_dashboard

    def create_revision_with_workflow(
        self,
        document_id: int,
        filename: str,
        file_content: BinaryIO,
        change_log: Optional[str],
        created_by: int,
        reviewer_id: Optional[int] = None,
        approver_id: Optional[int] = None,
        review_duration_days: int = 2,
        approval_duration_days: int = 1,
        major: bool = False,
    ) -> DocumentRevision:
        """Create revision with workflow tasks atomically.
        
        ALL operations are wrapped in a single transaction:
        - Revision creation
        - Workflow task creation (review + approval)
        - Dependency creation
        - CPM recalculation
        - Dashboard metrics update
        
        If ANY step fails, ALL changes are rolled back.
        """
        with self._db.transaction():
            # Step 1: Create revision (includes file storage, document status update)
            revision = self._revision_service.create_revision(
                document_id=document_id,
                filename=filename,
                file_content=file_content,
                change_log=change_log,
                created_by=created_by,
                major=major,
            )

            # Step 2: Validate document and project exist
            document = self._documents.get_by_id(document_id)
            if document is None:
                raise ValueError(f"Document {document_id} not found")

            project = self._projects.get_by_id(document.project_id)
            if project is None:
                raise ValueError(f"Project {document.project_id} not found")

            today = date.today()
            
            # Step 3: Create review task
            review_task = None
            if reviewer_id is not None:
                review_task = self._create_workflow_task(
                    project=project,
                    document=document,
                    revision=revision,
                    task_type=TaskType.REVIEW,
                    assigned_to=reviewer_id,
                    duration_days=review_duration_days,
                    start_date=today,
                )

            # Step 4: Create approval task with dependency on review
            if approver_id is not None:
                approval_start = review_task.end_date_planned if review_task else today
                approval_task = self._create_workflow_task(
                    project=project,
                    document=document,
                    revision=revision,
                    task_type=TaskType.APPROVAL,
                    assigned_to=approver_id,
                    duration_days=approval_duration_days,
                    start_date=approval_start,
                )

                if review_task:
                    self._deps.insert(
                        project_id=project.id,
                        predecessor_task_id=review_task.id,
                        successor_task_id=approval_task.id,
                    )

            # Step 5: Recalculate CPM (critical path method)
            # This is expensive but must be atomic with revision creation
            self._cpm.recalculate_project_schedule(project.id)
            
            # Step 6: Update dashboard metrics
            self._dashboard.recalculate_project_metrics(project.id)

            logger.info(
                "Workflow created for revision %d (doc=%d, reviewer=%s, approver=%s)",
                revision.id, document_id, reviewer_id, approver_id,
            )
            return revision

    def _create_workflow_task(
        self,
        project: object,
        document: object,
        revision: DocumentRevision,
        task_type: TaskType,
        assigned_to: int,
        duration_days: int,
        start_date: date,
    ):
        return self._tasks.insert(
            project_id=project.id,
            project_code=project.code,
            project_name=project.name,
            document_id=document.id,
            document_code=document.code,
            revision_id=revision.id,
            revision_index=revision.revision_index,
            name=f"{task_type.value.capitalize()} {document.code} {revision.revision_index}",
            task_type=task_type,
            assigned_to=assigned_to,
            owner_name=None,
            duration_days_planned=duration_days,
            work_hours_planned=float(duration_days * 8),
            start_date_planned=start_date,
            end_date_planned=start_date + timedelta(days=duration_days),
            status=TaskStatus.NOT_STARTED,
        )

    def approve_revision_with_workflow_dto(
        self,
        revision_id: int,
        approved_by: int,
        comment: Optional[str] = None,
    ) -> dict:
        """Approve revision with workflow task completion atomically.
        
        ALL operations are wrapped in a single transaction:
        - Revision approval
        - Approval task completion
        - Dashboard metrics update
        
        If ANY step fails, ALL changes are rolled back.
        """
        with self._db.transaction():
            # Step 1: Approve revision (includes document status update)
            self._revision_service.approve_revision(revision_id, approved_by)

            revision = self._revisions.get_by_id(revision_id)
            if revision is None:
                raise ValueError(f"Revision {revision_id} not found")

            # Step 2: Complete any approval tasks for this revision
            tasks = self._tasks.get_by_revision_id(revision_id)
            for task in tasks:
                if task.task_type == TaskType.APPROVAL and task.status != TaskStatus.COMPLETED:
                    self._tasks.update_progress(
                        task_id=task.id,
                        percent_complete=100,
                        start_date_actual=task.start_date_actual or date.today(),
                        end_date_actual=date.today(),
                        actual_hours=task.actual_hours,
                        status=TaskStatus.COMPLETED,
                    )

            # Step 3: Update dashboard metrics
            self._dashboard.recalculate_project_metrics(revision.document_id)

            document = self._documents.get_by_id(revision.document_id)
            logger.info(
                "Revision %d approved by user %d (comment: %s)",
                revision_id, approved_by, comment,
            )

            return {
                "revision_id": revision_id,
                "status": RevisionStatus.APPROVED.value,
                "approved_by": approved_by,
                "document_id": revision.document_id,
                "document_status": document.status.value if document else None,
            }

    def get_workflow_tasks_for_revision(
        self, revision_id: int
    ) -> RevisionWorkflowDTO:
        tasks = self._tasks.get_by_revision_id(revision_id)

        review_task_dto = None
        approval_task_dto = None

        for task in tasks:
            dto = WorkflowTaskDTO(
                task_id=task.id,
                name=task.name,
                task_type=task.task_type.value,
                assigned_to=task.assigned_to,
                status=task.status.value,
                start_date_planned=task.start_date_planned,
                end_date_planned=task.end_date_planned,
            )
            if task.task_type == TaskType.REVIEW:
                review_task_dto = dto
            elif task.task_type == TaskType.APPROVAL:
                approval_task_dto = dto

        return RevisionWorkflowDTO(
            review_task=review_task_dto,
            approval_task=approval_task_dto,
        )
