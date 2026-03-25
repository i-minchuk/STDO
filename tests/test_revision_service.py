"""Tests for RevisionService using mocks."""

from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock

from models.document import Document
from models.enums import DocumentStatus, RevisionStatus
from models.revision import DocumentRevision
from services.revision_service import RevisionService


def _make_document(doc_id: int = 1, status: DocumentStatus = DocumentStatus.IN_WORK):
    return Document(
        id=doc_id,
        project_id=1,
        code="DOC-001",
        title="Test",
        discipline="Piping",
        status=status,
        current_revision_id=None,
        created_by=1,
        created_at=datetime(2026, 1, 1),
    )


def _make_revision(rev_id: int = 1, version: int = 1, letter: str = "A", number: int = 1):
    return DocumentRevision(
        id=rev_id,
        document_id=1,
        revision_index=f"{letter}{number:02d}",
        revision_letter=letter,
        revision_number=number,
        version_number=version,
        status=RevisionStatus.DRAFT,
        file_path="/tmp/test.pdf",
        change_log="Test",
        created_by=1,
        created_at=datetime(2026, 1, 1),
        approved_by=None,
        approved_at=None,
    )


def test_create_first_revision():
    db = MagicMock()
    db.transaction.return_value.__enter__ = MagicMock(return_value=None)
    db.transaction.return_value.__exit__ = MagicMock(return_value=False)

    doc_repo = MagicMock()
    rev_repo = MagicMock()
    storage = MagicMock()

    doc_repo.get_by_id.return_value = _make_document()
    rev_repo.get_latest_version_number.return_value = 0
    rev_repo.insert.return_value = _make_revision()
    storage.save_revision_file.return_value = "/tmp/test.pdf"

    service = RevisionService(db, doc_repo, rev_repo, storage)
    revision = service.create_revision(
        document_id=1,
        filename="test.pdf",
        file_content=BytesIO(b"data"),
        change_log="Initial",
        created_by=1,
    )

    assert revision.revision_index == "A01"
    rev_repo.insert.assert_called_once()
    call_kwargs = rev_repo.insert.call_args
    assert call_kwargs.kwargs.get("revision_letter") or call_kwargs[1].get("revision_letter") == "A"
    doc_repo.update_current_revision.assert_called_once()


def test_create_minor_revision():
    db = MagicMock()
    db.transaction.return_value.__enter__ = MagicMock(return_value=None)
    db.transaction.return_value.__exit__ = MagicMock(return_value=False)

    doc_repo = MagicMock()
    rev_repo = MagicMock()
    storage = MagicMock()

    doc_repo.get_by_id.return_value = _make_document()
    rev_repo.get_latest_version_number.return_value = 1
    rev_repo.get_latest_letter_and_number.return_value = ("A", 1)
    rev_repo.insert.return_value = _make_revision(rev_id=2, version=2, letter="A", number=2)
    storage.save_revision_file.return_value = "/tmp/test2.pdf"

    service = RevisionService(db, doc_repo, rev_repo, storage)
    revision = service.create_revision(
        document_id=1,
        filename="test2.pdf",
        file_content=BytesIO(b"data"),
        change_log="Minor fix",
        created_by=1,
        major=False,
    )

    assert revision.revision_index == "A02"


def test_create_major_revision():
    db = MagicMock()
    db.transaction.return_value.__enter__ = MagicMock(return_value=None)
    db.transaction.return_value.__exit__ = MagicMock(return_value=False)

    doc_repo = MagicMock()
    rev_repo = MagicMock()
    storage = MagicMock()

    doc_repo.get_by_id.return_value = _make_document()
    rev_repo.get_latest_version_number.return_value = 2
    rev_repo.get_latest_letter_and_number.return_value = ("A", 2)
    rev_repo.insert.return_value = _make_revision(rev_id=3, version=3, letter="B", number=1)
    storage.save_revision_file.return_value = "/tmp/test3.pdf"

    service = RevisionService(db, doc_repo, rev_repo, storage)
    revision = service.create_revision(
        document_id=1,
        filename="test3.pdf",
        file_content=BytesIO(b"data"),
        change_log="Major change",
        created_by=1,
        major=True,
    )

    assert revision.revision_index == "B01"


def test_create_revision_document_not_found():
    db = MagicMock()
    db.transaction.return_value.__enter__ = MagicMock(return_value=None)
    db.transaction.return_value.__exit__ = MagicMock(return_value=False)

    doc_repo = MagicMock()
    rev_repo = MagicMock()
    storage = MagicMock()

    doc_repo.get_by_id.return_value = None

    service = RevisionService(db, doc_repo, rev_repo, storage)

    try:
        service.create_revision(
            document_id=999,
            filename="test.pdf",
            file_content=BytesIO(b"data"),
            change_log="Test",
            created_by=1,
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "999" in str(e)


def test_next_letter():
    assert RevisionService._next_letter("A") == "B"
    assert RevisionService._next_letter("Z") == "Z"
    assert RevisionService._next_letter("") == "A"
    assert RevisionService._next_letter("1") == "A"
