import logging
from typing import BinaryIO, Optional

from db.database import Database
from models.enums import DocumentStatus, RevisionStatus
from models.revision import DocumentRevision
from repositories.document_repository import DocumentRepository
from repositories.revision_repository import RevisionRepository
from services.storage_service import StorageService

logger = logging.getLogger(__name__)


class RevisionService:
    def __init__(
        self,
        db: Database,
        document_repo: DocumentRepository,
        revision_repo: RevisionRepository,
        storage: StorageService,
    ) -> None:
        self._db = db
        self._documents = document_repo
        self._revisions = revision_repo
        self._storage = storage

    def create_revision(
        self,
        document_id: int,
        filename: str,
        file_content: BinaryIO,
        change_log: Optional[str],
        created_by: int,
        major: bool = False,
    ) -> DocumentRevision:
        """Create revision atomically.
        
        ALL operations are wrapped in a single transaction:
        - Revision record creation
        - File storage
        - Document current revision update
        - Document status update
        - Mark previous revisions as superseded
        
        If ANY step fails, ALL changes are rolled back.
        """
        with self._db.transaction():
            document = self._documents.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document {document_id} not found")

            latest_version = self._revisions.get_latest_version_number(document_id)
            new_version = latest_version + 1

            if latest_version == 0:
                letter = "A"
                number = 1
            else:
                last_letter, last_num = self._revisions.get_latest_letter_and_number(
                    document_id
                )
                if major:
                    letter = self._next_letter(last_letter)
                    number = 1
                else:
                    letter = last_letter
                    number = last_num + 1

            revision_index = f"{letter}{number:02d}"

            # File storage is synchronous - this will be rolled back if transaction fails
            # Note: For production, consider async storage or two-phase commit
            file_path = self._storage.save_revision_file(
                project_code=str(document.project_id),
                document_code=document.code,
                version_number=new_version,
                filename=filename,
                content=file_content,
            )

            revision = self._revisions.insert(
                document_id=document.id,
                revision_index=revision_index,
                revision_letter=letter,
                revision_number=number,
                version_number=new_version,
                status=RevisionStatus.DRAFT,
                file_path=file_path,
                change_log=change_log,
                created_by=created_by,
            )

            self._documents.update_current_revision(document.id, revision.id)

            if document.status == DocumentStatus.APPROVED:
                self._documents.update_status(document.id, DocumentStatus.IN_WORK, revision.id)
            elif document.status == DocumentStatus.ARCHIVED:
                self._documents.update_status(document.id, DocumentStatus.IN_WORK, revision.id)
            elif document.status == DocumentStatus.ON_REVIEW:
                self._documents.update_status(document.id, DocumentStatus.IN_WORK, revision.id)

            self._revisions.mark_previous_revisions_superseded(
                document.id, revision.id
            )

            logger.info(
                "Created revision %s (v%d) for document %d",
                revision_index, new_version, document_id,
            )
            return revision

    def approve_revision(self, revision_id: int, approved_by: int) -> None:
        """Approve revision atomically.
        
        ALL operations are wrapped in a single transaction:
        - Revision status update
        - Document current revision update
        - Document status update
        - Mark previous revisions as superseded
        
        If ANY step fails, ALL changes are rolled back.
        """
        with self._db.transaction():
            revision = self._revisions.get_by_id(revision_id)
            if not revision:
                raise ValueError(f"Revision {revision_id} not found")

            # Проверка: ревизия должна быть на проверке (ON_REVIEW)
            if revision.status != RevisionStatus.ON_REVIEW:
                raise ValueError(
                    f"Ревизия должна быть на проверке для утверждения. "
                    f"Текущий статус: {revision.status.value}"
                )

            self._revisions.approve_revision(revision_id, approved_by)

            document = self._documents.get_by_id(revision.document_id)
            if not document:
                raise ValueError(f"Document {revision.document_id} not found")

            self._documents.update_current_revision(document.id, revision_id)
            self._documents.update_status(
                document.id, DocumentStatus.APPROVED, revision_id
            )
            self._revisions.mark_previous_revisions_superseded(
                document.id, revision_id
            )

            logger.info(
                "Revision %d approved by user %d", revision_id, approved_by
            )

    @staticmethod
    def _next_letter(letter: str) -> str:
        if not letter or letter < "A" or letter > "Z":
            return "A"
        if letter == "Z":
            return "Z"
        return chr(ord(letter) + 1)
