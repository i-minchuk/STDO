from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from core.auth import get_current_user
from core.service_locator import get_locator
from models.user import User

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("/")
def list_documents(
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    loc = get_locator()
    docs = loc.document_repo.get_all()
    if project_id:
        docs = [d for d in docs if d.project_id == project_id]
    if status:
        docs = [d for d in docs if d.status.value == status]
    if search:
        q = search.lower()
        docs = [d for d in docs if q in (d.title or "").lower() or q in (d.code or "").lower()]
    return [
        {
            "id": d.id,
            "code": d.code,
            "title": d.title,
            "project_id": d.project_id,
            "status": d.status.value,
            "discipline": d.discipline,
            "current_revision_id": d.current_revision_id,
        }
        for d in docs
    ]


@router.get("/{doc_id}")
def get_document(doc_id: int, current_user: User = Depends(get_current_user)):
    loc = get_locator()
    doc = loc.document_repo.get_by_id(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    revisions = loc.revision_repo.get_revisions_for_document(doc_id)
    return {
        "id": doc.id,
        "code": doc.code,
        "title": doc.title,
        "project_id": doc.project_id,
        "status": doc.status.value,
        "discipline": doc.discipline,
        "current_revision_id": doc.current_revision_id,
        "revisions": [
            {
                "id": r.id,
                "revision_index": r.revision_index,
                "revision_letter": r.revision_letter,
                "revision_number": r.revision_number,
                "status": r.status.value,
                "created_at": str(r.created_at) if r.created_at else None,
                "file_path": r.file_path,
            }
            for r in revisions
        ],
    }
