# services/revision_service.py
from typing import Optional, BinaryIO

from db.database import Database
from models.enums import RevisionStatus, DocumentStatus
from repositories.document_repository import DocumentRepository
from repositories.revision_repository import RevisionRepository
from services.storage_service import StorageService


class RevisionService:
    def __init__(
        self,
        db: Database,
        document_repo: DocumentRepository,
        revision_repo: RevisionRepository,
        storage: StorageService,
    ):
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
    ):
        with self._db.transaction():
            document = self._documents.get_by_id(document_id)
            if not document:
                raise ValueError(f"Document {document_id} not found")

            latest_version = self._revisions.get_latest_version_number(document_id)
            new_version = latest_version + 1

            last_letter, last_num = self._revisions.get_latest_letter_and_number(document_id)

            if latest_version == 0:
                letter = "A"
                number = 1
            else:
                if major:
                    letter = self._next_letter(last_letter)
                    number = 1
                else:
                    letter = last_letter
                    number = last_num + 1

            revision_index = self._combine_index(letter, number)

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
            if document.status in (DocumentStatus.APPROVED, DocumentStatus.ARCHIVED):
                self._documents.update_status(document.id, DocumentStatus.IN_WORK)

            self._revisions.mark_previous_revisions_superseded(document.id, revision.id)

            return revision

    def approve_revision(self, revision_id: int, approved_by: int):
        with self._db.transaction():
            revision = self._revisions.get_by_id(revision_id)
            if not revision:
                raise ValueError(f"Revision {revision_id} not found")

            self._revisions.approve_revision(revision_id, approved_by)
            document = self._documents.get_by_id(revision.document_id)
            if not document:
                raise ValueError(f"Document {revision.document_id} not found")

            self._documents.update_current_revision(document.id, revision_id)
            self._documents.update_status(document.id, DocumentStatus.APPROVED)
            self._revisions.mark_previous_revisions_superseded(document.id, revision_id)

    @staticmethod
    def _combine_index(letter: str, number: int) -> str:
        return f"{letter}{number:02d}"

    @staticmethod
    def _next_letter(letter: str) -> str:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if letter not in alphabet:
            return "A"
        idx = alphabet.index(letter)
        if idx == len(alphabet) - 1:
            return "Z"
        return alphabet[idx + 1]