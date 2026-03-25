import logging
from typing import Optional, Sequence

from db.database import Database
from models.document import Document
from models.enums import DocumentStatus
from repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, db: Database, document_repo: DocumentRepository) -> None:
        self._db = db
        self._documents = document_repo

    def get_document(self, document_id: int) -> Optional[Document]:
        return self._documents.get_by_id(document_id)

    def get_documents_for_project(self, project_id: int) -> Sequence[Document]:
        return self._documents.get_by_project_id(project_id)

    def update_document_status(
        self, document_id: int, status: DocumentStatus
    ) -> None:
        with self._db.transaction():
            self._documents.update_status(document_id, status)
            logger.info(
                "Document %d status updated to %s", document_id, status.value
            )
