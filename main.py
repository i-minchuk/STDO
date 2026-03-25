import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import load_config
from core.service_locator import init_locator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

cfg = load_config()


@asynccontextmanager
async def lifespan(application: FastAPI):
    locator = init_locator(cfg)
    logger.info("Application started — database connected")
    yield
    locator.db.close()
    logger.info("Application shutdown — database closed")


app = FastAPI(
    title="STDO — Document Management & CPM Planning",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.project_api import router as project_router  # noqa: E402
from api.revision_api import router as revision_router  # noqa: E402
from api.internal_project_api import router as internal_router  # noqa: E402

app.include_router(project_router)
app.include_router(revision_router)
app.include_router(internal_router, prefix="/api/internal", tags=["internal"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
