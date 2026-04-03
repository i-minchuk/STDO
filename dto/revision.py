from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from .common import DocumentShortDTO


class RevisionDTO(BaseModel):
    id: int
    document_id: int
    revision_index: str = Field(..., max_length=10)
    revision_letter: str = Field(..., max_length=1)
    revision_number: int = Field(..., ge=0)
    version_number: int = Field(..., ge=1)
    status: str
    file_name: Optional[str] = Field(None, max_length=255)
    file_path: Optional[str] = Field(None, max_length=1000)
    change_log: Optional[str] = Field(None, max_length=1000)
    created_by: int
    created_at: datetime
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None


class WorkflowTaskDTO(BaseModel):
    task_id: int
    name: str = Field(..., min_length=1, max_length=200)
    task_type: str
    assigned_to: Optional[int] = None
    status: str
    start_date_planned: Optional[date] = None
    end_date_planned: Optional[date] = None


class RevisionWorkflowDTO(BaseModel):
    review_task: Optional[WorkflowTaskDTO] = None
    approval_task: Optional[WorkflowTaskDTO] = None


class CreateRevisionRequestDTO(BaseModel):
    change_log: Optional[str] = Field(None, max_length=1000)
    created_by: int = Field(..., ge=1)
    major: bool = False
    reviewer_id: Optional[int] = Field(None, ge=1)
    approver_id: Optional[int] = Field(None, ge=1)
    review_duration_days: int = Field(2, ge=1, le=30)
    approval_duration_days: int = Field(1, ge=1, le=30)

    @field_validator('review_duration_days', 'approval_duration_days')
    @classmethod
    def validate_duration(cls, v):
        if v < 1 or v > 30:
            raise ValueError('Duration must be between 1 and 30 days')
        return v


class CreateRevisionResponseDTO(BaseModel):
    revision: RevisionDTO
    document: DocumentShortDTO
    workflow_tasks: RevisionWorkflowDTO


class ApproveRevisionRequestDTO(BaseModel):
    approved_by: int = Field(..., ge=1)
    comment: Optional[str] = Field(None, max_length=1000)