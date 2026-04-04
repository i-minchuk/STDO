from __future__ import annotations
from typing import Optional, List
from models.remark import Remark, RemarkResponse


class RemarkRepository:
    def __init__(self, db):
        self._db = db

    def get_by_project(self, project_id: int, status: Optional[str] = None) -> List[Remark]:
        sql = """
            SELECT r.id, r.project_id, r.document_id, r.revision_id,
                   r.author_id, ua.full_name,
                   r.assignee_id, ub.full_name,
                   r.source, r.text, r.status, r.resolution_comment,
                   r.created_at, r.resolved_at
            FROM remarks r
            LEFT JOIN users ua ON ua.id = r.author_id
            LEFT JOIN users ub ON ub.id = r.assignee_id
            WHERE r.project_id = %s
        """
        params: list = [project_id]
        if status:
            sql += " AND r.status = %s"
            params.append(status)
        sql += " ORDER BY r.created_at DESC"
        rows = self._db.fetch_all(sql, tuple(params))
        remarks = [Remark.from_row(r) for r in rows]
        # Подтягиваем ответы для каждого замечания
        for remark in remarks:
            remark.responses = self.get_responses(remark.id)
        return remarks

    def get_by_project_paginated(self, project_id: int, limit: int = 20, offset: int = 0, status: Optional[str] = None) -> tuple[List[Remark], int]:
        """Get project remarks with pagination.

        Returns:
            Tuple of (remarks list, total count)
        """
        sql = """
            SELECT r.id, r.project_id, r.document_id, r.revision_id,
                   r.author_id, ua.full_name,
                   r.assignee_id, ub.full_name,
                   r.source, r.text, r.status, r.resolution_comment,
                   r.created_at, r.resolved_at
            FROM remarks r
            LEFT JOIN users ua ON ua.id = r.author_id
            LEFT JOIN users ub ON ub.id = r.assignee_id
            WHERE r.project_id = %s
        """
        params: list = [project_id]
        if status:
            sql += " AND r.status = %s"
            params.append(status)
        sql += " ORDER BY r.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        rows = self._db.fetch_all(sql, tuple(params))
        remarks = [Remark.from_row(r) for r in rows]
        # Подтягиваем ответы для каждого замечания
        for remark in remarks:
            remark.responses = self.get_responses(remark.id)

        # Get total count
        count_sql = "SELECT count(*) AS cnt FROM remarks WHERE project_id = %s"
        count_params = [project_id]
        if status:
            count_sql += " AND status = %s"
            count_params.append(status)
        total_row = self._db.fetch_one(count_sql, tuple(count_params))
        total = int(total_row["cnt"]) if total_row else 0

        return remarks, total

    def get_responses(self, remark_id: int) -> List[RemarkResponse]:
        rows = self._db.fetch_all(
            """SELECT rr.id, rr.remark_id, rr.author_id, u.full_name, rr.text, rr.created_at
               FROM remark_responses rr
               JOIN users u ON u.id = rr.author_id
               WHERE rr.remark_id = %s ORDER BY rr.created_at""",
            (remark_id,),
        )
        return [RemarkResponse.from_row(r) for r in rows]

    def create(self, project_id: int, text: str, author_id: int,
               document_id: Optional[int] = None, revision_id: Optional[int] = None,
               assignee_id: Optional[int] = None, source: str = "internal") -> Remark:
        row = self._db.fetch_one(
            """INSERT INTO remarks (project_id, document_id, revision_id,
               author_id, assignee_id, source, text, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,'open')
               RETURNING id, project_id, document_id, revision_id,
               author_id, NULL, assignee_id, NULL,
               source, text, status, resolution_comment, created_at, resolved_at""",
            (project_id, document_id, revision_id, author_id, assignee_id, source, text),
        )
        return Remark.from_row(row)

    def update_status(self, remark_id: int, status: str,
                      resolution_comment: Optional[str] = None) -> Optional[Remark]:
        from datetime import datetime, timezone
        resolved_at = datetime.now(timezone.utc) if status != "open" else None
        self._db.execute(
            """UPDATE remarks SET status=%s, resolution_comment=%s, resolved_at=%s
               WHERE id=%s""",
            (status, resolution_comment, resolved_at, remark_id),
        )
        rows = self._db.fetch_all(
            """SELECT r.id, r.project_id, r.document_id, r.revision_id,
               r.author_id, ua.full_name, r.assignee_id, ub.full_name,
               r.source, r.text, r.status, r.resolution_comment,
               r.created_at, r.resolved_at
               FROM remarks r
               LEFT JOIN users ua ON ua.id = r.author_id
               LEFT JOIN users ub ON ub.id = r.assignee_id
               WHERE r.id = %s""",
            (remark_id,),
        )
        return Remark.from_row(rows[0]) if rows else None

    def add_response(self, remark_id: int, author_id: int, text: str) -> RemarkResponse:
        row = self._db.fetch_one(
            """INSERT INTO remark_responses (remark_id, author_id, text)
               VALUES (%s, %s, %s)
               RETURNING id, remark_id, author_id,
               (SELECT full_name FROM users WHERE id=%s), text, created_at""",
            (remark_id, author_id, text, author_id),
        )
        return RemarkResponse.from_row(row)