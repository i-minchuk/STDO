from __future__ import annotations
from typing import Optional, List
from repositories.remark_repository import RemarkRepository
from models.remark import Remark, RemarkResponse
from models.enums import RemarkStatus


VALID_STATUSES = {s.value for s in RemarkStatus}


class RemarkService:
    def __init__(self, remark_repo: RemarkRepository):
        self._repo = remark_repo

    def get_project_remarks(self, project_id: int,
                            status: Optional[str] = None) -> List[Remark]:
        return self._repo.get_by_project(project_id, status)

    def create_remark(self, project_id: int, text: str, author_id: int,
                      document_id: Optional[int] = None,
                      assignee_id: Optional[int] = None,
                      source: str = "internal") -> Remark:
        if not text.strip():
            raise ValueError("Текст замечания не может быть пустым")
        return self._repo.create(
            project_id, text.strip(), author_id,
            document_id=document_id, assignee_id=assignee_id, source=source,
        )

    def resolve_remark(self, remark_id: int, status: str,
                       comment: Optional[str] = None) -> Remark:
        if status not in VALID_STATUSES:
            raise ValueError(f"Недопустимый статус: {status}")
        if status == RemarkStatus.OPEN:
            raise ValueError("Нельзя вернуть статус 'open' через resolve")
        result = self._repo.update_status(remark_id, status, comment)
        if not result:
            raise ValueError(f"Замечание #{remark_id} не найдено")
        return result

    def add_response(self, remark_id: int, author_id: int, text: str) -> RemarkResponse:
        if not text.strip():
            raise ValueError("Текст ответа не может быть пустым")
        return self._repo.add_response(remark_id, author_id, text.strip())