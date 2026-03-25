# # core/service_locator.py
# from db.database import Database
# from core.settings import Settings
# from repositories.document_repository import DocumentRepository
# from repositories.revision_repository import RevisionRepository
# from repositories.planned_task_repository import PlannedTaskRepository
# from repositories.task_dependency_repository import TaskDependencyRepository
# from repositories.time_log_repository import TimeLogRepository
# from repositories.project_repository import ProjectRepository
# from repositories.engineer_metric_repository import EngineerMetricRepository
# from services.storage_service import StorageService
# from services.revision_service import RevisionService
# from services.document_service import DocumentService
# from services.cpm_scheduler_service import CPMSchedulerService
# from services.task_service import TaskService
# from services.today_tasks_service import TodayTasksService
# from services.project_dashboard_service import ProjectDashboardService
# from services.project_service import ProjectService
# from services.scheduling_client import SchedulingClient
# from services.queue_client import QueueClient
# from services.engineer_gamification_service import EngineerGamificationService
# from services.engineer_badge_service import EngineerBadgeService
# from services.engineer_dashboard_service import EngineerDashboardService


# class ServiceLocator:
#     def __init__(self, settings: Settings):
#         self._settings = settings
#         self.db = Database(settings.db_dsn)
#         self.db.connect()

#         self.storage = StorageService(settings.storage_root)
#         self.queue_client = QueueClient()  # реализация под конкретную очередь
#         self.scheduling_client = SchedulingClient(self.queue_client)

#         self.project_repo = ProjectRepository(self.db)
#         self.document_repo = DocumentRepository(self.db)
#         self.revision_repo = RevisionRepository(self.db)
#         self.task_repo = PlannedTaskRepository(self.db)
#         self.dep_repo = TaskDependencyRepository(self.db)
#         self.time_log_repo = TimeLogRepository(self.db)
#         self.metric_repo = EngineerMetricRepository(self.db)

#         self.revision_service = RevisionService(self.db, self.document_repo, self.revision_repo, self.storage)
#         self.document_service = DocumentService(self.db, self.document_repo)
#         self.cpm_scheduler = CPMSchedulerService(self.db, self.task_repo, self.dep_repo)
#         self.task_service = TaskService(self.db, self.task_repo, self.dep_repo, self.scheduling_client)
#         self.today_tasks_service = TodayTasksService(self.db, self.task_repo, self.dep_repo, self.time_log_repo)
#         self.project_dashboard_service = ProjectDashboardService(self.project_repo, self.task_repo, self.time_log_repo)
#         self.project_service = ProjectService(
#             self.db, self.project_repo, self.task_repo, self.time_log_repo, self.scheduling_client
#         )
#         self.engineer_gamification_service = EngineerGamificationService(
#             self.db, self.metric_repo, ..., self.task_repo, self.document_repo
#         )
#         self.engineer_badge_service = EngineerBadgeService(self.metric_repo, ..., ...)
#         self.engineer_dashboard_service = EngineerDashboardService(self.metric_repo, ..., ...)

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
    def __init__(self, cfg: Config):
        self.db = Database(cfg.db_dsn)
        self.db.connect()

        self.project_repo = ProjectRepository(self.db)
        self.document_repo = DocumentRepository(self.db)
        self.revision_repo = RevisionRepository(self.db)
        self.task_repo = PlannedTaskRepository(self.db)
        self.dep_repo = TaskDependencyRepository(self.db)

        self.storage = StorageService(cfg.storage_root)
        self.revision_service = RevisionService(self.db, self.document_repo, self.revision_repo, self.storage)
        self.document_service = DocumentService(self.db, self.document_repo)
        self.cpm_scheduler = CPMSchedulerService(self.db, self.task_repo, self.dep_repo)
        self.project_dashboard = ProjectDashboardService(self.project_repo, self.task_repo)

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