from typing import Optional, Sequence
from db.database import Database
from models.document import Document
from models.enums import DocumentStatus


class DocumentRepository:
    def __init__(self, db: Database):
        self._db = db

    def get_by_id(self, document_id: int) -> Optional[Document]:
        row = self._db.fetch_one(
            """
            SELECT id, project_id, code, title,
                   discipline, status,
                   current_revision_id,
                   created_by, created_at
            FROM documents
            WHERE id = %s
            """,
            (document_id,),
        )
        return self._row_to_model(row) if row else None

    def get_by_project_id(self, project_id: int) -> Sequence[Document]:
        rows = self._db.fetch_all(
            """
            SELECT id, project_id, code, title,
                   discipline, status,
                   current_revision_id,
                   created_by, created_at
            FROM documents
            WHERE project_id = %s
            ORDER BY code
            """,
            (project_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def insert(
        self,
        project_id: int,
        code: str,
        title: str,
        discipline: str | None,
        status: DocumentStatus,
        current_revision_id: int | None,
        created_by: int,
    ) -> Document:
        row = self._db.fetch_one(
            """
            INSERT INTO documents (
                project_id, code, title,
                discipline, status,
                current_revision_id,
                created_by
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            RETURNING id, project_id, code, title,
                      discipline, status,
                      current_revision_id,
                      created_by, created_at
            """,
            (
                project_id,
                code,
                title,
                discipline,
                status.value,
                current_revision_id,
                created_by,
            ),
        )
        return self._row_to_model(row)

    def update_status(
        self,
        document_id: int,
        status: DocumentStatus,
        current_revision_id: int | None,
    ) -> None:
        self._db.execute(
            """
            UPDATE documents
            SET status = %s,
                current_revision_id = %s
            WHERE id = %s
            """,
            (
                status.value,
                current_revision_id,
                document_id,
            ),
        )

    @staticmethod
    def _row_to_model(row: dict) -> Document:
        return Document(
            id=row["id"],
            project_id=row["project_id"],
            code=row["code"],
            title=row["title"],
            discipline=row["discipline"],
            status=DocumentStatus(row["status"]),
            current_revision_id=row["current_revision_id"],
            created_by=row["created_by"],
            created_at=row["created_at"],
        )