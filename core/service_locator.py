from config import Config
from db.database import Database
from repositories.project_repository import ProjectRepository
from repositories.document_repository import DocumentRepository
from repositories.revision_repository import RevisionRepository
from repositories.planned_task_repository import PlannedTaskRepository
from repositories.task_dependency_repository import TaskDependencyRepository
from repositories.remark_repository import RemarkRepository
from repositories.vdr_mdr_repository import VDRRepository, MDRRepository
from services.remark_service import RemarkService
from services.storage_service import StorageService
from services.revision_service import RevisionService
from services.document_service import DocumentService
from services.document_workflow_service import DocumentWorkflowService
from services.cpm_scheduler_service import CPMSchedulerService
from services.project_dashboard_service import ProjectDashboardService
from services.time_calculation_service import TimeCalculationService
from repositories.gamification_event_repository import GamificationEventRepository
from repositories.gamification_badge_repository import GamificationBadgeRepository
from repositories.notification_repository import NotificationRepository
from repositories.daily_quest_repository import DailyQuestRepository
from repositories.combo_achievement_repository import ComboAchievementRepository
from repositories.work_schedule_repository import WorkScheduleRepository


class ServiceLocator:
    """Application-level dependency container. Created once at startup."""

    def __init__(self, cfg: Config) -> None:
        # Initialize DB with connection pooling: min 2, max 10 concurrent connections
        self.db = Database(cfg.db_dsn, min_size=2, max_size=10)
        self.db.connect()

        # Repositories
        self.project_repo = ProjectRepository(self.db)
        self.document_repo = DocumentRepository(self.db)
        self.revision_repo = RevisionRepository(self.db)
        self.task_repo = PlannedTaskRepository(self.db)
        self.planned_task_repo = self.task_repo  # alias for API layer
        self.dep_repo = TaskDependencyRepository(self.db)
        self.user_repo = UserRepository(self.db)
        self.remark_repo = RemarkRepository(self.db)
        self.vdr_repo = VDRRepository(self.db)
        self.mdr_repo = MDRRepository(self.db)
        self.gamification_event_repo = GamificationEventRepository(self.db)
        self.gamification_badge_repo = GamificationBadgeRepository(self.db)
        self.notification_repo = NotificationRepository(self.db)
        self.daily_quest_repo = DailyQuestRepository(self.db)
        self.combo_achievement_repo = ComboAchievementRepository(self.db)
        self.work_schedule_repo = WorkScheduleRepository(self.db)

        # Services
        self.auth_service = AuthService(
            self.user_repo,
            secret_key=cfg.secret_key,
        )
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
        self.time_calculation = TimeCalculationService(self.work_schedule_repo)
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
        self.remark_service = RemarkService(self.remark_repo)

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
