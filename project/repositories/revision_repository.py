# repositories/revision_repository.py
from typing import Optional, Sequence
from datetime import datetime

from db.database import Database
from models.revision import DocumentRevision
from models.enums import RevisionStatus


class RevisionRepository:
    def __init__(self, db: Database):
        self._db = db

    async def get_by_id(self, revision_id: int) -> Optional[DocumentRevision]:
        row = await self._db.fetch_one(
            """
            SELECT id, document_id, revision_index, version_number, status,
                   file_path, change_log, created_by, created_at,
                   approved_by, approved_at
            FROM document_revisions
            WHERE id = %s
            """,
            (revision_id,),
        )
        return self._row_to_model(row) if row else None

    async def get_revisions_for_document(
        self, document_id: int
    ) -> Sequence[DocumentRevision]:
        rows = await self._db.fetch_all(
            """
            SELECT id, document_id, revision_index, version_number, status,
                   file_path, change_log, created_by, created_at,
                   approved_by, approved_at
            FROM document_revisions
            WHERE document_id = %s
            ORDER BY version_number DESC
            """,
            (document_id,),
        )
        return [self._row_to_model(r) for r in rows]

    async def get_latest_version_number(self, document_id: int) -> int:
        row = await self._db.fetch_one(
            """
            SELECT COALESCE(MAX(version_number), 0) AS max_version
            FROM document_revisions
            WHERE document_id = %s
            """,
            (document_id,),
        )
        return int(row["max_version"])

    async def insert(
            self,
            document_id: int,
            revision_index: str,
            revision_letter: str,
            revision_number: int,
            version_number: int,
            status: RevisionStatus,
            file_path: str,
            change_log: Optional[str],
            created_by: int,
        ) -> DocumentRevision:
            row = await self._db.fetch_one(
                """
                INSERT INTO document_revisions (
                    document_id,
                    revision_index,
                    revision_letter,
                    revision_number,
                    version_number,
                    status,
                    file_path,
                    change_log,
                    created_by
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, document_id, revision_index, revision_letter,
                        revision_number, version_number, status,
                        file_path, change_log, created_by, created_at,
                        approved_by, approved_at
                """,
                (
                    document_id,
                    revision_index,
                    revision_letter,
                    revision_number,
                    version_number,
                    status.value,
                    file_path,
                    change_log,
                    created_by,
                ),
            )
            return self._row_to_model(row)

    async def get_latest_for_document(self, document_id: int) -> Optional[DocumentRevision]:
        row = await self._db.fetch_one(
            """
            SELECT id, document_id, revision_index, revision_letter,
                   revision_number, version_number, status, file_path,
                   change_log, created_by, created_at, approved_by, approved_at
            FROM document_revisions
            WHERE document_id = %s
            ORDER BY version_number DESC
            LIMIT 1
            """,
            (document_id,),
        )
        return self._row_to_model(row) if row else None

    async def get_latest_letter_and_number(self, document_id: int) -> tuple[str, int]:
        row = await self._db.fetch_one(
            """
            SELECT COALESCE(MAX(revision_letter), 'A') AS last_letter,
                   COALESCE(MAX(revision_number), 0) AS last_number
            FROM document_revisions
            WHERE document_id = %s
            """,
            (document_id,),
        )
        return row["last_letter"], int(row["last_number"])

    async def mark_previous_revisions_superseded(self, document_id: int, exclude_id: int) -> None:
        await self._db.execute(
            """
            UPDATE document_revisions
            SET status = %s
            WHERE document_id = %s
              AND id <> %s
              AND status <> %s
            """,
            (
                RevisionStatus.SUPERSEDED.value,
                document_id,
                exclude_id,
                RevisionStatus.SUPERSEDED.value,
            ),
        )

    async def approve_revision(self, revision_id: int, approved_by: int) -> None:
        await self._db.execute(
            """
            UPDATE document_revisions
            SET status = %s,
                approved_by = %s,
                approved_at = %s
            WHERE id = %s
            """,
            (
                RevisionStatus.APPROVED.value,
                approved_by,
                datetime.utcnow(),
                revision_id,
            ),
        )

    @staticmethod
    def _row_to_model(row) -> DocumentRevision:
        return DocumentRevision(
            id=row["id"],
            document_id=row["document_id"],
            revision_index=row["revision_index"],
            revision_letter=row["revision_letter"],
            revision_number=row["revision_number"],
            version_number=row["version_number"],
            status=RevisionStatus(row["status"]),
            file_path=row["file_path"],
            change_log=row["change_log"],
            created_by=row["created_by"],
            created_at=row["created_at"],
            approved_by=row["approved_by"],
            approved_at=row["approved_at"],
        )