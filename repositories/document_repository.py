from typing import Optional, Sequence

from db.database import Database
from models.document import Document
from models.enums import DocumentStatus


class DocumentRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    _COLUMNS = """
        id, project_id, code, title, discipline, status,
        current_revision_id, created_by, created_at
    """

    def get_by_id(self, document_id: int) -> Optional[Document]:
        row = self._db.fetch_one(
            f"SELECT {self._COLUMNS} FROM documents WHERE id = %s",
            (document_id,),
        )
        return self._row_to_model(row) if row else None

    def get_by_project_id(self, project_id: int) -> Sequence[Document]:
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM documents WHERE project_id = %s ORDER BY code",
            (project_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def get_all(self) -> Sequence[Document]:
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM documents ORDER BY code"
        )
        return [self._row_to_model(r) for r in rows]

    def get_all_paginated(self, limit: int = 20, offset: int = 0) -> tuple[Sequence[Document], int]:
        """List all documents with pagination.

        Returns:
            Tuple of (documents list, total count)
        """
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM documents ORDER BY code LIMIT %s OFFSET %s",
            (limit, offset),
        )
        documents = [self._row_to_model(r) for r in rows]

        # Get total count
        total_row = self._db.fetch_one("SELECT count(*) AS cnt FROM documents")
        total = int(total_row["cnt"]) if total_row else 0

        return documents, total

    def get_by_project_id_paginated(self, project_id: int, limit: int = 20, offset: int = 0) -> tuple[Sequence[Document], int]:
        """List documents by project with pagination.

        Returns:
            Tuple of (documents list, total count)
        """
        rows = self._db.fetch_all(
            f"SELECT {self._COLUMNS} FROM documents WHERE project_id = %s ORDER BY code LIMIT %s OFFSET %s",
            (project_id, limit, offset),
        )
        documents = [self._row_to_model(r) for r in rows]

        # Get total count
        total_row = self._db.fetch_one(
            "SELECT count(*) AS cnt FROM documents WHERE project_id = %s",
            (project_id,),
        )
        total = int(total_row["cnt"]) if total_row else 0

        return documents, total

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
            INSERT INTO documents (project_id, code, title, discipline, status,
                                   current_revision_id, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING {self._COLUMNS}
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
            """
            UPDATE documents
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
            "UPDATE documents SET current_revision_id = %s WHERE id = %s",
            (revision_id, document_id),
        )

    def count_by_project_and_status(
        self, project_id: int, status: DocumentStatus
    ) -> int:
        row = self._db.fetch_one(
            "SELECT count(*) AS cnt FROM documents WHERE project_id = %s AND status = %s",
            (project_id, status.value),
        )
        return int(row["cnt"]) if row else 0

    @staticmethod
    def _row_to_model(row: dict) -> Document:
        return Document(
            id=row["id"],
            project_id=row["project_id"],
            code=row["code"],
            title=row["title"],
            discipline=row.get("discipline"),
            status=DocumentStatus(row["status"]),
            current_revision_id=row.get("current_revision_id"),
            created_by=row["created_by"],
            created_at=row["created_at"],
        )
