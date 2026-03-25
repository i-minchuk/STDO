# # main.py
# from __future__ import annotations
# import tkinter as tk

# from core.service_locator import ServiceLocator
# from ui.main_window import MainWindow

# from config import CONFIG
# from core.settings_service import SettingsService
# from services.storage_service import StorageService
# from services.revision_service import RevisionService
# from repositories.document_repository import DocumentRepository
# from repositories.revision_repository import RevisionRepository
# from db.database import Database
# from services.document_service import DocumentService
# from core.event_bus import EventBus


# def init_services() -> None:
#     settings = SettingsService(CONFIG)
#     ServiceLocator.register("settings", settings)

#     db = Database(settings.db_path)
#     ServiceLocator.register("db", db)

#     doc_repo = DocumentRepository(db)
#     rev_repo = RevisionRepository(db)
#     ServiceLocator.register("document_repository", doc_repo)
#     ServiceLocator.register("revision_repository", rev_repo)

#     storage = StorageService(settings)
#     ServiceLocator.register("storage_service", storage)

#     event_bus = EventBus()
#     doc_service = DocumentService(doc_repo, event_bus)
#     ServiceLocator.register("document_service", doc_service)

#     revision_service = RevisionService(rev_repo, doc_repo)
#     ServiceLocator.register("revision_service", revision_service)

#     # сюда же позже добавишь planner, analytics и др.


# def main() -> None:
#     init_services()

#     root = tk.Tk()
#     root.title("Technical Documentation Tracker")

#     app = MainWindow(root)
#     app.pack(fill=tk.BOTH, expand=True)

#     root.mainloop()


# if __name__ == "__main__":
#     main()

from fastapi import FastAPI
from config import load_config
from core.service_locator import ServiceLocator
from api.project_api import router as project_router
from api.revision_api import router as revision_router
from api.internal_project_api import router as internal_router


cfg = load_config()
locator = ServiceLocator(cfg)

app = FastAPI(title="DMS/CPM MVP")

# dependency
def get_locator() -> ServiceLocator:
    return locator

app.include_router(project_router)
app.include_router(revision_router)
app.include_router(internal_router, prefix="/api/internal", tags=["internal"])
