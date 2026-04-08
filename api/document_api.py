from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from core.auth import get_current_user
from core.service_locator import get_locator
from models.user import User
from dto.pagination import PaginatedResponse
from dto.document import DocumentDetailDTO, DocumentListDTO, RevisionShortDTO
from models.enums import DocumentStatus
from repositories.document_repository import DocumentRepository
from repositories.revision_repository import RevisionRepository

router = APIRouter(prefix="/api/documents", tags=["documents"])


def get_document_repo() -> DocumentRepository:
    return get_locator().document_repo


def get_revision_repo() -> RevisionRepository:
    return get_locator().revision_repo


@router.get("/", response_model=PaginatedResponse[DocumentListDTO])
def list_documents(
    document_repo: DocumentRepository = Depends(get_document_repo),
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(20, gt=0, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[DocumentListDTO]:
    """List documents with pagination support."""
    parsed_status = None
    if status is not None:
        try:
            parsed_status = DocumentStatus(status)
        except ValueError as exc:
            raise HTTPException(400, f"Invalid document status: {status}") from exc

    docs, total = document_repo.search_paginated(
        project_id=project_id,
        status=parsed_status,
        search=search,
        limit=limit,
        offset=offset,
    )

    items = [
        DocumentListDTO(
            id=d.id,
            code=d.code,
            title=d.title,
            project_id=d.project_id,
            status=d.status,
            discipline=d.discipline,
            current_revision_id=d.current_revision_id,
        )
        for d in docs
    ]

    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{doc_id}", response_model=DocumentDetailDTO)
def get_document(
    doc_id: int,
    document_repo: DocumentRepository = Depends(get_document_repo),
    revision_repo: RevisionRepository = Depends(get_revision_repo),
    current_user: User = Depends(get_current_user),
) -> DocumentDetailDTO:
    loc = get_locator()
    doc = document_repo.get_by_id(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    revisions = revision_repo.get_revisions_for_document(doc_id)
    return DocumentDetailDTO(
        id=doc.id,
        code=doc.code,
        title=doc.title,
        project_id=doc.project_id,
        status=doc.status,
        discipline=doc.discipline,
        current_revision_id=doc.current_revision_id,
        revisions=[
            RevisionShortDTO(
                id=r.id,
                revision_index=r.revision_index,
                revision_letter=r.revision_letter,
                revision_number=r.revision_number,
                status=r.status,
                created_at=r.created_at,
                file_path=r.file_path,
            )
            for r in revisions
        ],
    )
