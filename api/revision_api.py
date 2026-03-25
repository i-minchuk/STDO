from fastapi import APIRouter, Depends, UploadFile, File
from io import BytesIO
from core.service_locator import ServiceLocator, get_locator
from dto.revision import (
    CreateRevisionRequestDTO,
    CreateRevisionResponseDTO,
    ApproveRevisionRequestDTO,
    RevisionDTO,
    RevisionWorkflowDTO,
)
from dto.common import DocumentShortDTO

router = APIRouter(prefix="/api", tags=["revisions"])


@router.post("/documents/{document_id}/revisions", response_model=CreateRevisionResponseDTO)
def create_revision(
    document_id: int,
    meta: CreateRevisionRequestDTO,
    file: UploadFile = File(...),
    locator: ServiceLocator = Depends(get_locator),
):
    wf = locator.document_workflow

    revision = wf.create_revision_with_workflow(
        document_id=document_id,
        filename=file.filename,
        file_content=BytesIO(file.file.read()),
        change_log=meta.change_log,
        created_by=meta.created_by,
        reviewer_id=meta.reviewer_id,
        approver_id=meta.approver_id,
        review_duration_days=meta.review_duration_days,
        approval_duration_days=meta.approval_duration_days,
        major=meta.major,
    )

    doc = locator.document_repo.get_by_id(document_id)
    project = locator.project_repo.get_by_id(doc.project_id)

    document_dto = DocumentShortDTO(
        id=doc.id,
        project_id=doc.project_id,
        project_code=project.code,
        code=doc.code,
        title=doc.title,
        status=doc.status.value,
        current_revision_id=doc.current_revision_id,
    )

    # здесь можно достать review/approval задачи и собрать RevisionWorkflowDTO
    wf_tasks = wf.get_workflow_tasks_for_revision(revision.id)

    return CreateRevisionResponseDTO(
        revision=RevisionDTO(
            id=revision.id,
            document_id=revision.document_id,
            revision_index=revision.revision_index,
            revision_letter=revision.revision_letter,
            revision_number=revision.revision_number,
            version_number=revision.version_number,
            status=revision.status.value,
            file_name=file.filename,
            file_path=revision.file_path,
            change_log=revision.change_log,
            created_by=revision.created_by,
            created_at=revision.created_at,
            approved_by=revision.approved_by,
            approved_at=revision.approved_at,
        ),
        document=document_dto,
        workflow_tasks=wf_tasks,
    )


@router.post("/revisions/{revision_id}/approve")
def approve_revision(
    revision_id: int,
    body: ApproveRevisionRequestDTO,
    locator: ServiceLocator = Depends(get_locator),
):
    wf = locator.document_workflow
    response_dto = wf.approve_revision_with_workflow_dto(
        revision_id=revision_id,
        approved_by=body.approved_by,
        comment=body.comment,
    )
    return response_dto