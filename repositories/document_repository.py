from typing import Optional, Sequence
from db.database import Database
from models.document import Document
from models.enums import DocumentStatus
from repositories.base_repository import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    _COLUMNS = """
        id, project_id, code, title, discipline, status,
        current_revision_id, created_by, created_at
    """

    def __init__(self, db: Database) -> None:
        super().__init__(db, Document, "documents", self._COLUMNS)

    def get_by_project_id(self, project_id: int) -> Sequence[Document]:
        rows = self._db.fetch_all(
            f"SELECT {self._columns} FROM {self._table_name} WHERE project_id = %s ORDER BY code",
            (project_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def get_all(self) -> Sequence[Document]:
        return self.list_all(order_by="code")

    def search_paginated(
        self,
        project_id: int | None = None,
        status: DocumentStatus | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Sequence[Document], int]:
        """List documents with filtering applied at database level."""
        where_clauses: list[str] = []
        params: list[object] = []

        if project_id is not None:
            where_clauses.append("project_id = %s")
            params.append(project_id)

        if status is not None:
            where_clauses.append("status = %s")
            params.append(status.value)

        if search:
            where_clauses.append("(LOWER(title) LIKE %s OR LOWER(code) LIKE %s)")
            pattern = f"%{search.lower()}%"
            params.extend([pattern, pattern])

        where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        return self._get_paginated(
            where_sql=where_sql,
            params=tuple(params),
            order_by="code",
            limit=limit,
            offset=offset
        )

    def insert(
        self,
        project_id: int,
        code: str,
        title: str,
        discipline: str | None,
        status: DocumentStatus,
        created_by: int,
        current_revision_id: int | None = None,
    ) -> Document:
        row = self._db.fetch_one(
            f"""
            INSERT INTO {self._table_name} (project_id, code, title, discipline, status,
                                   current_revision_id, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING {self._columns}
            """,
            (project_id, code, title, discipline, status.value,
             current_revision_id, created_by),
        )
        return self._row_to_model(row)

    def update_status(
        self,
        document_id: int,
        status: DocumentStatus,
        current_revision_id: int | None = None,
    ) -> None:
        self._db.execute(
            f"""
            UPDATE {self._table_name}
            SET status = %s,
                current_revision_id = COALESCE(%s, current_revision_id)
            WHERE id = %s
            """,
            (status.value, current_revision_id, document_id),
        )

    def update_current_revision(
        self, document_id: int, revision_id: int
    ) -> None:
        self._db.execute(
            f"UPDATE {self._table_name} SET current_revision_id = %s WHERE id = %s",
            (revision_id, document_id),
        )

    def count_by_project_and_status(
        self, project_id: int, status: DocumentStatus
    ) -> int:
        row = self._db.fetch_one(
            f"SELECT count(*) AS cnt FROM {self._table_name} WHERE project_id = %s AND status = %s",
            (project_id, status.value),
        )
        return int(row["cnt"]) if row else 0

    def _row_to_model(self, row: dict) -> Document:
        # Override to handle DocumentStatus Enum conversion
        row["status"] = DocumentStatus(row["status"])
        return super()._row_to_model(row)
