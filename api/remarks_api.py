from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from core.auth import require_role
from core.service_locator import get_locator
from models.user import User
from api.gamification_api import award_gamification_with_badges

router = APIRouter(prefix="/api/remarks", tags=["remarks"])


class CreateRemarkRequest(BaseModel):
    project_id: int
    text: str
    document_id: Optional[int] = None
    assignee_id: Optional[int] = None
    source: str = "internal"


class ResolveRemarkRequest(BaseModel):
    status: str          # resolved / rejected / superseded
    comment: Optional[str] = None


class AddResponseRequest(BaseModel):
    text: str


@router.get("/project/{project_id}")
def get_project_remarks(
    project_id: int,
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_role("admin", "manager", "engineer", "norm_controller")),
):
    loc = get_locator()
    remarks = loc.remark_service.get_project_remarks(project_id, status)
    return [_remark_to_dict(r) for r in remarks]


@router.post("/")
def create_remark(
    body: CreateRemarkRequest,
    current_user: User = Depends(require_role("admin", "manager", "engineer", "norm_controller")),
):
    loc = get_locator()
    try:
        remark = loc.remark_service.create_remark(
            project_id=body.project_id,
            text=body.text,
            author_id=current_user.id,
            document_id=body.document_id,
            assignee_id=body.assignee_id,
            source=body.source,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Award gamification points for creating remarks
    if body.source.lower() == "crs":
        # Penalty for CRS remarks (unresolved issues returned)
        award_gamification_with_badges(
            locator=loc,
            user_id=current_user.id,
            event_type="crs_remark_created",
            points=-5,
            project_id=body.project_id,
            comment=f"Создано замечание CRS: {body.text[:50]}...",
        )
    else:
        # Regular remark creation (could be positive or neutral)
        award_gamification_with_badges(
            locator=loc,
            user_id=current_user.id,
            event_type="remark_created",
            points=0,  # Neutral for regular remarks
            project_id=body.project_id,
            comment=f"Создано замечание: {body.text[:50]}...",
        )

    return _remark_to_dict(remark)


@router.patch("/{remark_id}/resolve")
def resolve_remark(
    remark_id: int,
    body: ResolveRemarkRequest,
    current_user: User = Depends(require_role("admin", "manager", "engineer")),
):
    loc = get_locator()
    try:
        remark = loc.remark_service.resolve_remark(remark_id, body.status, body.comment)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return _remark_to_dict(remark)


@router.post("/{remark_id}/responses")
def add_response(
    remark_id: int,
    body: AddResponseRequest,
    current_user: User = Depends(require_role("admin", "manager", "engineer")),
):
    loc = get_locator()
    try:
        response = loc.remark_service.add_response(remark_id, current_user.id, body.text)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {
        "id": response.id, "remark_id": response.remark_id,
        "author_name": response.author_name, "text": response.text,
        "created_at": response.created_at.isoformat(),
    }


def _remark_to_dict(r) -> dict:
    return {
        "id": r.id, "project_id": r.project_id,
        "document_id": r.document_id, "source": r.source,
        "text": r.text, "status": r.status,
        "author_name": r.author_name, "assignee_name": r.assignee_name,
        "resolution_comment": r.resolution_comment,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
        "responses": [
            {"id": rs.id, "author_name": rs.author_name,
             "text": rs.text, "created_at": rs.created_at.isoformat()}
            for rs in r.responses
        ],
    }