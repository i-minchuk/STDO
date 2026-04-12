from __future__ import annotations
from typing import List, Optional
from models.vdr_mdr import VDREntry, MDREntry
from datetime import datetime, timezone

from db.database import Database
from repositories.base_repository import BaseRepository


class VDRRepository(BaseRepository[VDREntry]):
    """Repository for VDR entries with BaseRepository for CRUD operations.
    
    Migrated to BaseRepository to reduce boilerplate.
    Custom methods: upsert, get_by_project, get_by_project_paginated
    """
    
    def __init__(self, db: Database) -> None:
        super().__init__(
            db=db,
            model_class=VDREntry,
            table_name="vdr_entries",
            columns="id, project_id, doc_number, title, discipline, responsible_contractor, latest_revision, latest_upload_date, status, is_auto_filled, created_at, updated_at"
        )

    def upsert(self, project_id: int, doc_number: str, title: str,
               discipline: Optional[str], contractor: Optional[str],
               revision: Optional[str], upload_date: datetime,
               status: Optional[str]) -> VDREntry:
        row = self._db.fetch_one(
            f"""INSERT INTO {self._table_name}
               (project_id, doc_number, title, discipline, responsible_contractor,
                latest_revision, latest_upload_date, status, updated_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,now())
               ON CONFLICT (project_id, doc_number) DO UPDATE SET
                   latest_revision = EXCLUDED.latest_revision,
                   latest_upload_date = EXCLUDED.latest_upload_date,
                   status = EXCLUDED.status,
                   updated_at = now()
               RETURNING {self._columns}""",
            (project_id, doc_number, title, discipline, contractor,
             revision, upload_date, status),
        )
        return self._row_to_model(row)

    def get_by_project(self, project_id: int) -> List[VDREntry]:
        rows = self._db.fetch_all(
            f"SELECT {self._columns} FROM {self._table_name} WHERE project_id=%s ORDER BY doc_number",
            (project_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def get_by_project_paginated(self, project_id: int, limit: int = 20, offset: int = 0) -> tuple[List[VDREntry], int]:
        """Get VDR entries for project with pagination.

        Returns:
            Tuple of (entries list, total count)
        """
        return self._get_paginated(
            where_sql=" WHERE project_id=%s",
            params=(project_id,),
            order_by="doc_number",
            limit=limit,
            offset=offset
        )


class MDRRepository(BaseRepository[MDREntry]):
    """Repository for MDR entries with BaseRepository for CRUD operations.
    
    Migrated to BaseRepository to reduce boilerplate.
    Custom methods: upsert, get_by_project, get_by_project_paginated
    """
    
    def __init__(self, db: Database) -> None:
        super().__init__(
            db=db,
            model_class=MDREntry,
            table_name="mdr_entries",
            columns="id, project_id, doc_number, title, discipline, revision_current, planned_issue_date, actual_issue_date, status, is_auto_filled, created_at, updated_at"
        )

    def upsert(self, project_id: int, doc_number: str, title: str,
               discipline: Optional[str], revision: Optional[str],
               status: Optional[str]) -> MDREntry:
        row = self._db.fetch_one(
            f"""INSERT INTO {self._table_name}
               (project_id, doc_number, title, discipline, revision_current, status, updated_at)
               VALUES (%s,%s,%s,%s,%s,%s,now())
               ON CONFLICT (project_id, doc_number) DO UPDATE SET
                   revision_current = EXCLUDED.revision_current,
                   status = EXCLUDED.status,
                   updated_at = now()
               RETURNING {self._columns}""",
            (project_id, doc_number, title, discipline, revision, status),
        )
        return self._row_to_model(row)

    def get_by_project(self, project_id: int) -> List[MDREntry]:
        rows = self._db.fetch_all(
            f"SELECT {self._columns} FROM {self._table_name} WHERE project_id=%s ORDER BY doc_number",
            (project_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def get_by_project_paginated(self, project_id: int, limit: int = 20, offset: int = 0) -> tuple[List[MDREntry], int]:
        """Get MDR entries for project with pagination.

        Returns:
            Tuple of (entries list, total count)
        """
        return self._get_paginated(
            where_sql=" WHERE project_id=%s",
            params=(project_id,),
            order_by="doc_number",
            limit=limit,
            offset=offset
        )