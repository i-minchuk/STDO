"""ДокПоток IRIS — Система управления инженерной документацией. Entry point."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import Config
from core.service_locator import init_locator, get_locator

logger = logging.getLogger("ДокПоток IRIS")

# Rate limiter configuration: 100 requests per minute per IP
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = Config()  # ← теперь работает, т.к. у Config есть дефолты
    logging.basicConfig(
        level=getattr(logging, cfg.log_level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )

    # Run database migrations before initializing the app
    from db.migrations_runner import run_migrations
    run_migrations()

    init_locator(cfg)
    logger.info("ДокПоток IRIS v0.3.0 started")
    try:
        yield
    finally:
        get_locator().db.close()
        logger.info("ДокПоток IRIS stopped")


app = FastAPI(
    title="ДокПоток IRIS API",
    version="0.3.0",
    description="Система учёта технической документации",
    lifespan=lifespan,
)

# Add rate limiter to FastAPI app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
from api.remarks_api import router as remarks_router
from api.reports_api import router as reports_router
from api.vdr_mdr_api import router as vdr_mdr_router
from api.admin_api import router as admin_router

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
app.include_router(remarks_router)
app.include_router(reports_router)
app.include_router(vdr_mdr_router)
app.include_router(admin_router)

# --- Serve frontend build (Vite) ---

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if os.path.isdir(FRONTEND_DIST):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """
        Catch-all: всё, что не /api/* и не /assets/* → index.html.
        SPA-роутинг на фронте.
        """
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path, media_type="text/html")
        return {"error": "Frontend build not found"}


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.3.0"}
