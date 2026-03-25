from config import Config
from db.database import Database
from repositories.project_repository import ProjectRepository
from repositories.document_repository import DocumentRepository
from repositories.revision_repository import RevisionRepository
from repositories.planned_task_repository import PlannedTaskRepository
from repositories.task_dependency_repository import TaskDependencyRepository
from services.storage_service import StorageService
from services.revision_service import RevisionService
from services.document_service import DocumentService
from services.document_workflow_service import DocumentWorkflowService
from services.cpm_scheduler_service import CPMSchedulerService
from services.project_dashboard_service import ProjectDashboardService


class ServiceLocator:
    """Application-level dependency container. Created once at startup."""

    def __init__(self, cfg: Config) -> None:
        self.db = Database(cfg.db_dsn)
        self.db.connect()

        # Repositories
        self.project_repo = ProjectRepository(self.db)
        self.document_repo = DocumentRepository(self.db)
        self.revision_repo = RevisionRepository(self.db)
        self.task_repo = PlannedTaskRepository(self.db)
        self.dep_repo = TaskDependencyRepository(self.db)

        # Services
        self.storage = StorageService(cfg.storage_root)
        self.revision_service = RevisionService(
            self.db, self.document_repo, self.revision_repo, self.storage,
        )
        self.document_service = DocumentService(self.db, self.document_repo)
        self.cpm_scheduler = CPMSchedulerService(
            self.db, self.task_repo, self.dep_repo,
        )
        self.project_dashboard = ProjectDashboardService(
            self.project_repo, self.task_repo,
        )
        self.document_workflow = DocumentWorkflowService(
            self.db,
            self.revision_service,
            self.document_repo,
            self.revision_repo,
            self.project_repo,
            self.task_repo,
            self.dep_repo,
            self.cpm_scheduler,
            self.project_dashboard,
        )


# Module-level singleton — set by main.py at startup
_locator: ServiceLocator | None = None


def init_locator(cfg: Config) -> ServiceLocator:
    global _locator
    _locator = ServiceLocator(cfg)
    return _locator


def get_locator() -> ServiceLocator:
    if _locator is None:
        raise RuntimeError("ServiceLocator not initialized. Call init_locator() first.")
    return _locator
