"""STDO — Система учёта технической документации. Entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Config
from core.service_locator import init_locator, get_locator

logger = logging.getLogger("stdo")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )
    cfg = Config()
    init_locator(cfg)
    logger.info("STDO v0.3.0 started")
    yield
    get_locator().db.close()
    logger.info("STDO stopped")


app = FastAPI(
    title="STDO API",
    version="0.3.0",
    description="Система учёта технической документации",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
from api.auth_api import router as auth_router
from api.project_api import router as project_router
from api.document_api import router as document_router
from api.revision_api import router as revision_router
from api.task_api import router as task_router
from api.dashboard_api import router as dashboard_router
from api.gamification_api import router as gamification_router
from api.users_api import router as users_router
from api.internal_project_api import router as internal_router
from api.import_api import router as import_router
from api.workload_api import router as workload_router
from api.tender_api import router as tender_router

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(document_router)
app.include_router(revision_router)
app.include_router(task_router)
app.include_router(dashboard_router)
app.include_router(gamification_router)
app.include_router(users_router)
app.include_router(internal_router)
app.include_router(import_router)
app.include_router(workload_router)
app.include_router(tender_router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.3.0"}
