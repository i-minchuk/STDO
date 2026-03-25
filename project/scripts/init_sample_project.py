# scripts/init_sample_project.py
from datetime import date

from config import load_config
from db.database import Database
from repositories.project_repository import ProjectRepository
from repositories.document_repository import DocumentRepository
from repositories.revision_repository import RevisionRepository
from repositories.planned_task_repository import PlannedTaskRepository
from models.enums import ProjectStatus, DocumentStatus, TaskStatus, TaskType


def main():
    cfg = load_config()
    db = Database(cfg.db_dsn)
    db.connect()

    project_repo = ProjectRepository(db)
    doc_repo = DocumentRepository(db)
    rev_repo = RevisionRepository(db)
    task_repo = PlannedTaskRepository(db)

    with db.transaction():
        # 1. создаём проект
        project = project_repo.insert(
            code="PRJ-PIPE-001",
            name="Газопровод Северный",
            customer="ГазИнвест",
            status=ProjectStatus.ACTIVE,
            manager_id=2,  # Мария из миграции
            start_date=date(2026, 1, 10),
            end_date_planned=date(2026, 9, 30),
        )
        print("Project id:", project.id)

        # 2. создаём документ
        doc = doc_repo.insert(
            project_id=project.id,
            code="P&ID-1001",
            title="P&ID Насосная станция",
            discipline="Piping",
            status=DocumentStatus.IN_WORK,
            created_by=1,  # Иван
        )
        print("Document id:", doc.id)

        # 3. создаём одну инженерную задачу под этот документ
        task = task_repo.insert(
            project=project,
            document=doc,
            revision_id=None,
            revision_index=None,
            name="ENG P&ID-1001",
            task_type=TaskType.ENGINEERING,
            assigned_to=1,
            owner_name="Иван Петров",
            duration_days_planned=5,
            work_hours_planned=40.0,
            start_date_planned=date(2026, 3, 25),
            end_date_planned=date(2026, 3, 30),
            status=TaskStatus.NOT_STARTED,
        )
        print("Task id:", task.id)

    db.close()


if __name__ == "__main__":
    main()