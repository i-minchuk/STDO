import logging
import os
from typing import BinaryIO

logger = logging.getLogger(__name__)


class StorageService:
    """Stores revision files on the local filesystem."""

    def __init__(self, storage_root: str) -> None:
        self._root = storage_root
        os.makedirs(self._root, exist_ok=True)

    def save_revision_file(
        self,
        project_code: str,
        document_code: str,
        version_number: int,
        filename: str,
        content: BinaryIO,
    ) -> str:
        safe_project = self._sanitize(project_code)
        safe_doc = self._sanitize(document_code)
        directory = os.path.join(self._root, safe_project, safe_doc)
        os.makedirs(directory, exist_ok=True)

        stored_name = f"v{version_number:04d}_{filename}"
        path = os.path.join(directory, stored_name)

        with open(path, "wb") as f:
            while chunk := content.read(8192):
                f.write(chunk)

        logger.info("Saved revision file: %s", path)
        return path

    def file_exists(self, path: str) -> bool:
        return os.path.isfile(path)

    @staticmethod
    def _sanitize(name: str) -> str:
        return "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
