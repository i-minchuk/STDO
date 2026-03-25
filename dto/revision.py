from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from .common import DocumentShortDTO


class RevisionDTO(BaseModel):
    id: int
    document_id: int
    revision_index: str
    revision_letter: str
    revision_number: int
    version_number: int
    status: str
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    change_log: Optional[str] = None
    created_by: int
    created_at: datetime
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None


class WorkflowTaskDTO(BaseModel):
    task_id: int
    name: str
    task_type: str
    assigned_to: Optional[int] = None
    status: str
    start_date_planned: Optional[date] = None
    end_date_planned: Optional[date] = None


class RevisionWorkflowDTO(BaseModel):
    review_task: Optional[WorkflowTaskDTO] = None
    approval_task: Optional[WorkflowTaskDTO] = None


class CreateRevisionRequestDTO(BaseModel):
    change_log: Optional[str] = None
    created_by: int
    major: bool = False
    reviewer_id: Optional[int] = None
    approver_id: Optional[int] = None
    review_duration_days: int = 2
    approval_duration_days: int = 1


class CreateRevisionResponseDTO(BaseModel):
    revision: RevisionDTO
    document: DocumentShortDTO
    workflow_tasks: RevisionWorkflowDTO


class ApproveRevisionRequestDTO(BaseModel):
    approved_by: int
    comment: Optional[str] = None