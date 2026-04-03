from __future__ import annotations
from fastapi import APIRouter, Depends
from core.auth import require_role
from core.service_locator import get_locator
from models.user import User

router = APIRouter(prefix="/api", tags=["vdr-mdr"])


@router.get("/projects/{project_id}/vdr")
def get_vdr(project_id: int,
            current_user: User = Depends(require_role("admin", "manager", "engineer"))):
    loc = get_locator()
    entries = loc.vdr_repo.get_by_project(project_id)
    return [{"id": e.id, "doc_number": e.doc_number, "title": e.title,
             "discipline": e.discipline, "latest_revision": e.latest_revision,
             "status": e.status, "latest_upload_date": e.latest_upload_date,
             "is_auto_filled": e.is_auto_filled} for e in entries]


@router.get("/projects/{project_id}/mdr")
def get_mdr(project_id: int,
            current_user: User = Depends(require_role("admin", "manager", "engineer"))):
    loc = get_locator()
    entries = loc.mdr_repo.get_by_project(project_id)
    return [{"id": e.id, "doc_number": e.doc_number, "title": e.title,
             "discipline": e.discipline, "revision_current": e.revision_current,
             "status": e.status, "is_auto_filled": e.is_auto_filled} for e in entries]